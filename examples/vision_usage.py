"""Vision (multimodal) usage example for langchain-iointelligence.

io Intelligence exposes OpenAI-compatible vision models through the same
chat completions endpoint. Use ``vision_message()`` to combine a text
prompt with one or more images (remote URLs, local files or raw bytes).

Run with IO_API_KEY / IO_API_URL set in your environment or .env file.
"""

from dotenv import load_dotenv

from langchain_iointelligence import (
    DEFAULT_VISION_MODEL,
    IOIntelligenceChatModel,
    VISION_MODELS,
    vision_message,
)

# Load environment variables
load_dotenv()

IMAGE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/"
    "640px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
)


def main():
    """Vision usage example."""
    print("🖼️  langchain-iointelligence Vision Example")
    print("=" * 50)
    print(f"Available vision models: {', '.join(VISION_MODELS)}")
    print(f"Using: {DEFAULT_VISION_MODEL}\n")

    # A vision-capable model must be selected explicitly.
    chat = IOIntelligenceChatModel(model=DEFAULT_VISION_MODEL)

    # --- Remote image URL -------------------------------------------------
    message = vision_message("What is in this image?", IMAGE_URL)
    print("📝 Prompt: What is in this image?")
    print("\n🤖 Response:")
    try:
        response = chat.invoke([message])
        print(response.content)
    except Exception as e:  # noqa: BLE001
        print(f"❌ Error: {e}")
        print("Make sure IO_API_KEY and IO_API_URL are set in your .env file")

    # --- Local file / multiple images ------------------------------------
    # vision_message also accepts a local path, raw bytes, or a list of any
    # mix of URLs / paths / bytes (base64 data URLs are built automatically):
    #
    #   message = vision_message("Compare these", ["a.jpg", "b.png"])
    #   message = vision_message("Describe", image_bytes)  # bytes -> data URL


if __name__ == "__main__":
    main()
