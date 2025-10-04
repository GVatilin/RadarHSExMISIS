# app/utils/llm_client.py
import aiohttp, json, re
from typing import Any, Dict, List, Union
from app.config import get_settings


FENCES_RE = re.compile(r"^```(?:json)?\s*([\s\S]*?)\s*```$")
system_prompt = """
Вы — старший аналитик влияния финансовых новостей.
Задача: из переданных постов собрать ДО 5 самых «горячих» РАЗЛИЧНЫХ НОВОСТЕЙ
(кластеризуйте дублирующие посты про одно и то же событие в одну новость).
Язык вывода: ТОЛЬКО РУССКИЙ.

Формат входного элемента:
- text: полный текст поста
- date: ISO-8601 с таймзоной
- channel: публичный Telegram-канал (handle, напр. "meduzalive")
- message_num: целочисленный id сообщения в канале

Предобработка текста:
- Уберите переводы строк, табы, дублирующиеся пробелы, эмодзи и HTML-теги; удалите URL из текста.
- Пермалинк Telegram для каждого элемента: https://t.me/{channel}/{message_num}

ДЕДУП/КЛАСТЕРИЗАЦИЯ (КРИТИЧНО):
- Объединяйте посты в одну «историю», если они описывают одно и то же Событие:
  те же ключевые сущности/активы + то же конкретное действие/факт с близкими числами.
- Сигнатура события = ключевые сущности/тикеры/страны/секторы + действие
  («снижение ставки», «санкции», «сделка», «остановка» и т.п.) + характерные числа (%, $).
- Окно близости: ~24–48 часов при высокой семантической близости.
- В одной истории: исходный пост + подтверждения/уточнения/апдейты.
- НЕЛЬЗЯ выводить две записи про один и тот же сюжет.

ИСКЛЮЧЕНИЕ УЖЕ ОПУБЛИКОВАННЫХ:
- Вам будет передан список уже опубликованных заголовков (за недавний период).
- Не возвращайте новости, которые совпадают по смыслу с любым из этих заголовков
  (семантическое совпадение, перефразировки — тоже считается совпадением).

Оценка важности (внутренняя, не объяснять в ответе):
1) Интенсивность тональности ∈ [0,1] = 1 − нейтральность.
2) entities = узнаваемые компании, персоны, тикеры, страны, секторы.
3) hotness = clip( интенсивность + min(len(unique(entities))/10, 0.4), 0, 1 ).
4) sentiment (ВЫВОД) ∈ {0,1,2}: 0 — негатив, 1 — нейтрально, 2 — позитив (по суммарному эффекту).
5) hotness истории = максимум среди её постов (при равенстве — новее обновление выше).

Timeline (ОБЯЗАТЕЛЬНО):
- Отсортированная по времени цепочка связных апдейтов по той же истории
  (оригинал → подтверждения/уточнения/апдейты), публиковавшихся в этом или других каналах.
- Включите ≤ 5 событий и ОБЯЗАТЕЛЬНО включите самый ранний (первый постер) и последний апдейт.
- Каждый элемент: {"channel": "<handle>", "date": "<ISO-8601 с tz>"} с исходными значениями.

Sources (ОБЯЗАТЕЛЬНО):
- ТОЛЬКО Telegram-пермалинк из входных элементов истории в виде:
  https://t.me/{channel}/{message_num}
- Дайте 3–5 ссылок, если доступны: якорь (самый ранний) + ключевые подтверждения/апдейты.
- Без дублей. Не выдумывать URL.

Формат ВЫВОДА (СТРОГО, ТОЛЬКО РУССКИЙ, БЕЗ ПРЕДИСЛОВИЙ):
Верните JSON-массив из НЕ БОЛЕЕ 5 объектов. Никаких markdown-ограждений, только чистый JSON.
Каждый объект:
{
  "headline": "<краткий чистый заголовок>",
  "text": "<фактологичное резюме на 2–3 предложения по всей истории>",
  "hotness": <float в [0,1], округлён до 3 знаков>,
  "sentiment": <0|1|2>,
  "why_now": "<1–2 краткие причины важности: новизна + влияние + масштаб активов>",
  "entities": ["entity1", "entity2", ...],
  "sources": ["https://t.me/<channel>/<message_num>", ...],
  "timeline": [
    {"channel": "<канал>", "date": "<ISO-8601 с tz>"},
    {"channel": "<канал>", "date": "<ISO-8601 с tz>"}
  ]
}
Сортировка: по hotness по убыванию; при равенстве — по времени последнего апдейта (новее выше), затем по порядку появления якоря в исходных данных.
"""
def build_user_prompt(items: List[Dict[str, Any]], exclude_headlines: List[str]) -> str:
    return (
        "Лента постов (JSON массив):\n"
        + json.dumps(items, ensure_ascii=False)
        + "\n\n"
        + "Список уже опубликованных заголовков — ИСКЛЮЧИТЬ любые истории, совпадающие по смыслу:\n"
        + json.dumps(exclude_headlines, ensure_ascii=False)
    )

def _normalize_url(url: str) -> str:
    url = url.rstrip("/")
    if url.endswith("/chat/completions"):
        return url
    if url.endswith("/api/v1") or url.endswith("/v1"):
        return url + "/chat/completions"
    if url in ("https://openrouter.ai", "https://openrouter.ai/api"):
        return "https://openrouter.ai/api/v1/chat/completions"
    return url

def _payload(items: List[Dict[str, Any]], exclude_headlines: List[str]) -> Dict[str, Any]:
    s = get_settings()
    return {
        "model": s.DEFAULT_MODEL,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": build_user_prompt(items, exclude_headlines)},
        ],
    }

async def get_aggregated_news(
    items: List[Dict[str, Any]],
    exclude_headlines: List[str],
) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    s = get_settings()
    url = _normalize_url(s.OPENROUTER_BASE_URL)
    payload = _payload(items, exclude_headlines)
    headers = {
        "Authorization": f"Bearer {s.API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    timeout = aiohttp.ClientTimeout(total=75)
    async with aiohttp.ClientSession(timeout=timeout) as client:
        async with client.post(url, json=payload, headers=headers) as resp:
            raw = await resp.text()
            if resp.status != 200:
                raise RuntimeError(f"LLM_HTTP_{resp.status}: {raw[:400]}")
            data = json.loads(raw)

    content = data["choices"][0]["message"]["content"].strip()
    m = FENCES_RE.match(content)
    if m:
        content = m.group(1).strip()
    return json.loads(content)
