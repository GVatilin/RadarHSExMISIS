import asyncio
from llm_client import call_qwen

async def main():
    question = "Explain quantum tunneling in one sentence."
    system = "You are a helpful physics professor."

    reply = await call_qwen(question, system)
    print("Ответ:", reply)

if __name__ == "__main__":
    asyncio.run(main())