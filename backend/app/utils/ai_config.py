from uuid import uuid4
from pathlib import Path
from typing import Optional, Union


ai_url = "https://api.deepseek.com/chat/completions"
ai_model = "deepseek-chat"


async def get_headers(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }


async def payload_test():
    return {
        "model": ai_model,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Объяснение задачи для модели"
                )
            },
            {
                "role": "user",
                "content": f'ввод пользователя'
            },
        ],
    }
