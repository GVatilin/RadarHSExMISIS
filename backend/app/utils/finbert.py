import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN")
HF_INFERENCE_PROVIDER = "hf-inference"
DEFAULT_FINBERT_MODEL = "ProsusAI/finbert"

API_NOT_INITIALIZED_ERROR = "[ОШИБКА API] HF_TOKEN не задан."
API_GENERAL_ERROR = "[ОШИБКА API] Произошла ошибка при обращении к HuggingFace."


def call_finbert(text: str, model: Optional[str] = None) -> List[Dict[str, float]]:
    """Классифицирует тональность текста FinBERT."""
    if not HF_TOKEN:
        return [{"label": API_NOT_INITIALIZED_ERROR, "score": 0.0}]

    try:
        client = InferenceClient(
            provider=HF_INFERENCE_PROVIDER,
            api_key=HF_TOKEN,
        )
        # аргументы только именованные!
        res = client.text_classification(text=text, model=model or DEFAULT_FINBERT_MODEL)
        return {res[0]['label'] : res[0]['score'],
                res[1]['label'] : res[1]['score'],
                res[2]['label'] : res[2]['score']}
    except Exception as e:
        return API_GENERAL_ERROR


if __name__ == "__main__":
    sample = (
        "🚨 UPDATE: ZachXBT says the WhiteRock engineer rumored to have "
        "“passed away by a missile” is still active. Previously, founder "
        "Ildar Ilham was arrested in the UAE over the $30M ZKasino scam."
    )

    labels = call_finbert(sample)

    print(labels)
