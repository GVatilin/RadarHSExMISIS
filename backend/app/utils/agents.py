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
    You are a senior financial news-impact analyst.  
    Your only task: pick exactly 5 hottest stories from the provided list.

    Pre-processing: strip every headline & body of \n, \t, \r, extra spaces; remove emojis, HTML tags, URLs.

    Scoring rules (do NOT explain them, only use):
    1. Sentiment intensity: absolute sentiment polarity × confidence (0-1).  
       Range: 0 (neutral) → 1 (extreme positive/negative).
    2. Breadth score: (# unique A-level entities mentioned) ÷ 10.  
       A-level entities = globally recognisable persons, Fortune-500 companies, G20 governments.
    3. Composite heat = sentiment_intensity + breadth_score.  
       Clip to 0–1 range.

    Output format: strict JSON list of 5 objects, no preamble, no markdown fences.  
    Each object:
    {
      "rank": 1-5,
      "title": "<cleaned exact headline> (not very long)",
      "message": "<cleaned summary in 2-3 sentenceses>",
      "heat": <0.xxx rounded 3 decimals>,
      "why_now": "<1-2 short phrases: novelty + impact + asset scale>"
    }
    Sort descending by heat; resolve ties by original list order.
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