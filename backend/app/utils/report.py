import json
from app.config import get_settings
import aiohttp


def get_payload_report(posts):
    system_prompt = """
You are a senior financial-news impact analyst.
Your only task: pick exactly 5 hottest stories from the provided list.

Input format: each item has
  text: str        – full news text
  date: ISO-8601 datetime with tz
  channel: str     – source name
  message_num: int – unique id inside channel

Pre-processing: strip every text of \n, \t, \r, extra spaces; remove emojis, HTML tags, URLs.

Scoring (do NOT explain, only use):
1. sentiment = 1 − neutrality_score (0 = neutral, 1 = extreme positive/negative).
2. entities = globally recognisable companies, people, tickers, countries, sectors found in text.
3. hotness = sentiment + min(len(entities)/10, 0.4)  – clip to 0–1.
4. timeline — an ordered, time-sorted chain of related updates on the same story (original → confirmations/clarifications/updates), 
published by this channel or other channels, where each event records that a similar/continuing item on the same topic was posted.
include <= 5 events and must include the earliest (first poster) and the latest update.

Output: strict JSON list of 5 objects, no preamble, no markdown fences.
Each object:
{
  "headline": "<cleaned exact headline extracted from text, not very long>",
  "text": "<cleaned summary of text, 2-3 sentences>",
  "hotness": <0.xxx rounded 3 decimals>,
  "sentiment": <integer in {0,1,2} where 0 = negative, 1 = neutral, 2 = positive>,
  "why_now": "<1-2 short phrases: novelty + impact + asset scale>",
  "entities": ["entity1", "entity2", ...],
  "sources": ["<original channel>"],
  "timeline": [{"channel": "<channel>", "date": "<ISO-8601 with tz>"}]
}
Sort descending by hotness; ties broken by original list order.
Preserve original date, channel, message_num for every selected item.
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