import os
import asyncio
from typing import Optional

from dotenv import load_dotenv
from openai import (
    RateLimitError,
    APIConnectionError,
    APIStatusError,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

load_dotenv()

DEFAULT_MODEL = os.getenv("DEFAULT_MODEL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL: str = os.getenv(
    "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
)

API_NOT_INITIALIZED_ERROR = "[ОШИБКА API] Клиент OpenRouter не инициализирован."
API_RATE_LIMIT_ERROR = "[ОШИБКА API] Превышен лимит запросов к API."
API_CONNECTION_ERROR = "[ОШИБКА API] Не удалось подключиться к API."
API_GENERAL_ERROR = "[ОШИБКА API] Произошла ошибка при обращении к API."


async def call_llm(
    prompt_text: str,
    system_instruction: str = "",
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> str:
    """
    Асинхронно обращается к OpenRouter и возвращает ответ модели.
    """
    if not OPENROUTER_API_KEY:
        return API_NOT_INITIALIZED_ERROR

    try:
        llm = ChatOpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY,
            model=model or DEFAULT_MODEL,
            temperature=temperature,
        )

        messages = []
        if system_instruction:
            messages.append(SystemMessage(content=system_instruction))
        messages.append(HumanMessage(content=prompt_text))

        # В langchain-openai >= 0.1 агент уже поддерживает awaitable-интерфейс
        response = await llm.ainvoke(messages)
        return response.content.strip()

    except RateLimitError:
        return API_RATE_LIMIT_ERROR
    except APIConnectionError:
        return API_CONNECTION_ERROR
    except APIStatusError as e:
        return f"{API_GENERAL_ERROR} (Статус: {e.status_code})"
    except Exception as e:
        return f"{API_GENERAL_ERROR} {e}"


async def call_qwen(
    user_prompt: str,
    system_instruction: str = "",
    model: Optional[str] = None,
    temperature: float = 0.0,
) -> str:
    """
    Удобная обёртка поверх call_llm (по аналогии с вашей старой call_qwen).
    """
    return await call_llm(
        prompt_text=user_prompt,
        system_instruction=system_instruction,
        model=model or DEFAULT_MODEL,
        temperature=temperature,
    )


# Если нужен «скриптовый» запуск из консоли
async def main():
    question = "Explain quantum tunneling in one sentence."
    system = "You are a helpful physics professor."

    reply = await call_qwen(question, system)
    print("Ответ:", reply)

if __name__ == "__main__":
    asyncio.run(main())
