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
