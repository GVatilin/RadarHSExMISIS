import json
from app.config import get_settings
import aiohttp


def get_payload_report(posts):
    system_prompt = """
You are a senior financial-news impact analyst.
Your only task: from the provided items produce EXACTLY 5 hottest DISTINCT news stories
(i.e., cluster near-duplicate posts about the same underlying event into a single story).
OUTPUT LANGUAGE: RUSSIAN ONLY. All fields ("headline", "text", "why_now") must be in Russian.

Input format: each item has
  text: str        – full news text
  date: ISO-8601 datetime with tz
  channel: str     – source name
  message_num: int – unique id inside channel

Pre-processing:
- Strip newlines/tabs and duplicate spaces; remove emojis and HTML tags; remove URLs from text (but keep channel/message_num).
- Build a Telegram permalink for every item as: https://t.me/{channel}/{message_num}

DE-DUP / STORY CLUSTERING (CRITICAL):
- Group items into stories describing the SAME underlying event (same entities/assets + same concrete development).
- Event signature = key entities/tickers/countries/sectors + action (“cut rates”, “sanctions”, “merger”, “halt”, etc.) + salient numbers (%, $).
- Consider items in a reasonable time window (≈24–48h) with high semantic overlap as one story.
- A story aggregates all related items (original + confirmations/clarifications/updates). Do NOT output two objects for the same story.

Scoring (do NOT explain, only use):
1) sentiment_intensity ∈ [0,1] = 1 − neutrality_score.
2) entities = globally recognisable companies, people, tickers, countries, sectors found in text.
3) hotness = clip( sentiment_intensity + min(len(unique(entities))/10, 0.4), 0, 1 ).
4) sentiment (output) = integer in {0,1,2}: 0 = negative, 1 = neutral, 2 = positive (overall impact for the story).
5) Story hotness = MAX hotness among its items (ties → recency of latest update).

Timeline (REQUIRED, per story):
- Ordered, time-sorted chain of related updates on the same story (original → confirmations/clarifications/updates), published by this or other channels; include ≤ 5 events and MUST include the earliest (first poster) and the latest update.
- Each event is {"channel": str, "date": ISO-8601} and preserves original values.

Sources (REQUIRED, per story; RUSSIAN TEXT NOT NEEDED INSIDE LINKS):
- Form ONLY from Telegram permalinks of items in the story using the exact pattern:
  https://t.me/{channel}/{message_num}
- Include 3–5 links when available: anchor (earliest) + key confirmations/updates (unique, no duplicates).
- Do NOT fabricate or include non-Telegram links.

For each distinct story, produce (RUSSIAN ONLY):
{
  "headline": "<краткий чистый заголовок>",
  "text": "<сжатое фактологичное резюме на 2–3 предложения по всей истории>",
  "hotness": <float в [0,1], округлён до 3 знаков>,
  "sentiment": <integer in {0,1,2}>,
  "why_now": "<1–2 короткие фразы: новизна + влияние + масштаб активов>",
  "entities": ["entity1", "entity2", ...],   // уникальные по кластеру
  "sources": ["https://t.me/<channel>/<message_num>", ...],  // только такие ссылки
  "timeline": [
    {"channel": "<канал-источник>", "date": "<ISO-8601 с tz>"},
    {"channel": "<канал-подтверждение>", "date": "<ISO-8601 с tz>"}
  ]
}

Output:
- STRICT JSON array of EXACTLY 5 objects, no preamble, no markdown fences, no extra fields.
- Sort by hotness desc; ties → by latest update time (newer first), then by anchor order in input.
- Preserve original date/channel/message_num only inside timeline/sources.
    """

    user_prompt = f"""
News feed (JSON array):
{json.dumps(posts, ensure_ascii=False, indent=0)}

Return only the final JSON list.
    """

    return {
        "model": get_settings().DEFAULT_MODEL,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            },
        ],
    }

async def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


async def get_top_k(posts):
    s = get_settings()
    ai_url = s.OPENROUTER_BASE_URL

    payload = get_payload_report(posts)
    headers = await get_headers(get_settings().API_KEY)
    async with aiohttp.ClientSession() as client:
        async with client.post(ai_url, json=payload, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                res = data["choices"][0]["message"]["content"]
                if res.startswith("```json"):
                    res = res[7:-3].strip()
                res = json.loads(res)
                return res
            else:
                return f"check_error, status: {resp.status}"