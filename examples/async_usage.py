"""Async usage example for langchain-iointelligence.

Native async (ainvoke / astream / abatch) on top of httpx.
Run with IO_API_KEY / IO_API_URL set in your environment or .env file.
"""

import asyncio

from dotenv import load_dotenv

from langchain_iointelligence import IOIntelligenceChatModel

load_dotenv()

MODEL = "meta-llama/Llama-3.3-70B-Instruct"


async def main():
    chat = IOIntelligenceChatModel(model=MODEL)

    print("⚡ ainvoke")
    print("=" * 50)
    resp = await chat.ainvoke("Give me a one-line fun fact about octopuses.")
    print(resp.content)
    if resp.usage_metadata:
        print("tokens:", resp.usage_metadata)

    print("\n⚡ astream (with usage on the final chunk)")
    print("=" * 50)
    usage = None
    async for chunk in chat.astream("Count from one to five."):
        print(chunk.content, end="", flush=True)
        if chunk.usage_metadata:
            usage = chunk.usage_metadata
    print()
    print("stream usage:", usage)

    print("\n⚡ abatch (concurrent)")
    print("=" * 50)
    results = await chat.abatch(["Say hi", "Say hello", "Say hey"])
    for r in results:
        print("-", r.content)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {e}")
        print("Make sure IO_API_KEY and IO_API_URL are set in your .env file")
