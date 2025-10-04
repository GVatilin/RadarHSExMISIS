from llm_client import call_qwen
from finbert import call_finbert
import json


def agent_theme_of_the_day(hottest_news_list):
    system_prompt = """
    """

    user_prompt = """
    """

    response = call_qwen(user_prompt=user_prompt, system_instruction=system_prompt)

    try:
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:-3].strip()
        elif clean_response.startswith('```'):
            clean_response = clean_response[3:-3].strip()

        return json.loads(clean_response)
    except json.JSONDecodeError:
        return "Failed to parse LLM response as JSON"
    except Exception as e:
        return "Failed to parse LLM response as JSON"


def agent_top_k_hottest_news(hottest_news_list):
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

Output: strict JSON list of 5 objects, no preamble, no markdown fences.
Each object:
{
  "headline": "<cleaned exact headline extracted from text, not very long>",
  "text": "<cleaned summary of text, 2-3 sentences>",
  "hotness": <0.xxx rounded 3 decimals>,
  "sentiment": <0.xxx rounded 3 decimals>,
  "why_now": "<1-2 short phrases: novelty + impact + asset scale>",
  "entities": ["entity1", "entity2", ...],
  "sources": ["<original channel>"],
  "timeline": "<original ISO-8601 date string>"
}
Sort descending by hotness; ties broken by original list order.
Preserve original date, channel, message_num for every selected item.
    """

    user_prompt = f"""
News feed (JSON array):
{json.dumps(hottest_news_list, ensure_ascii=False, indent=0)}

Return only the final JSON list.
    """

    response = call_qwen(user_prompt=user_prompt, system_instruction=system_prompt)

    try:
        clean_response = response.strip()
        if clean_response.startswith('```json'):
            clean_response = clean_response[7:-3].strip()
        elif clean_response.startswith('```'):
            clean_response = clean_response[3:-3].strip()
        return json.loads(clean_response)
    except json.JSONDecodeError:
        return "Failed to parse LLM response as JSON"
    except Exception as e:
        return "Failed to parse LLM response as JSON"