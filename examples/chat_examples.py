"""Modern ChatModel usage examples with fallbacks and runtime switching."""

import os

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from langchain_iointelligence import IOIntelligenceChat

# Load environment variables
load_dotenv()


def basic_chat_example():
    """Basic ChatModel usage example."""
    print("🤖 Basic ChatModel Example")
    print("=" * 50)

    # Initialize chat model
    chat = IOIntelligenceChat(
        model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.7, max_tokens=500
    )

    # Single message
    messages = [HumanMessage(content="Tell me a fun fact about space exploration.")]

    try:
        response = chat.invoke(messages)
        print(f"🚀 Response: {response.content}")
        print(f"📊 Model: {response.response_metadata.get('model', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error: {e}")


def conversation_example():
    """Multi-turn conversation example."""
    print("\n💬 Multi-turn Conversation Example")
    print("=" * 50)

    chat = IOIntelligenceChat(temperature=0.8)

    # Multi-turn conversation
    messages = [
        SystemMessage(content="You are a helpful science teacher."),
        HumanMessage(content="What is photosynthesis?"),
    ]

    try:
        # First response
        response1 = chat.invoke(messages)
        print(f"🌱 Teacher: {response1.content[:200]}...")

        # Continue conversation
        messages.extend(
            [
                response1,  # Add AI response to conversation
                HumanMessage(content="Can you explain it more simply for a 10-year-old?"),
            ]
        )

        response2 = chat.invoke(messages)
        print(f"👶 Simplified: {response2.content[:200]}...")

    except Exception as e:
        print(f"❌ Error: {e}")


def modern_chain_example():
    """Modern LangChain chain example."""
    print("\n🔗 Modern Chain Example")
    print("=" * 50)

    # Create components
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a creative story writer. Write engaging short stories."),
            ("human", "Write a short story about {theme} in exactly {word_count} words."),
        ]
    )

    chat = IOIntelligenceChat(temperature=0.9)
    parser = StrOutputParser()  # Extract string from AIMessage

    # Modern chain: prompt | chat | parser
    chain = prompt | chat | parser

    try:
        story = chain.invoke({"theme": "a robot learning to paint", "word_count": "50"})
        print(f"📖 Generated Story:\n{story}")
    except Exception as e:
        print(f"❌ Error: {e}")


def streaming_example():
    """Streaming response example (if supported)."""
    print("\n📡 Streaming Example")
    print("=" * 50)

    chat = IOIntelligenceChat(temperature=0.7)
    messages = [HumanMessage(content="Count from 1 to 10 with a fun fact about each number.")]

    try:
        # Note: This uses the _stream method which currently just yields the full response
        # In a real streaming implementation, this would yield chunks
        print("🔢 Streaming response:")
        for chunk in chat._stream(messages):
            print(f"Chunk: {chunk.message.content[:100]}...")
    except Exception as e:
        print(f"❌ Error: {e}")


def fallback_example():
    """Fallback configuration example."""
    print("\n🛡️ Fallback Example")
    print("=" * 50)

    try:
        # Primary model
        primary = IOIntelligenceChat(
            model="meta-llama/Llama-3.3-70B-Instruct", timeout=5  # Short timeout for demo
        )

        # Note: In a real scenario, you'd have other providers as fallbacks
        # For this demo, we'll just show the concept
        print("Primary model configured with fallback capability")
        print("(In production, add ChatOpenAI or ChatAnthropic as fallbacks)")

        # Test primary model
        messages = [HumanMessage(content="Hello from the primary model!")]
        response = primary.invoke(messages)
        print(f"✅ Primary model response: {response.content[:100]}...")

    except Exception as e:
        print(f"❌ Primary model failed: {e}")
        print("🔄 (Fallback would trigger here in production setup)")


def runtime_config_example():
    """Runtime configuration example."""
    print("\n⚙️ Runtime Configuration Example")
    print("=" * 50)

    # Different model configurations
    models = {
        "creative": IOIntelligenceChat(
            model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.9, max_tokens=200
        ),
        "analytical": IOIntelligenceChat(
            model="meta-llama/Llama-3.3-70B-Instruct", temperature=0.1, max_tokens=300
        ),
    }

    prompt = "Explain artificial intelligence"

    for mode, chat in models.items():
        try:
            print(f"\n🧠 {mode.capitalize()} Mode:")
            messages = [HumanMessage(content=prompt)]
            response = chat.invoke(messages)
            print(f"Response: {response.content[:150]}...")
        except Exception as e:
            print(f"❌ Error in {mode} mode: {e}")


def main():
    """Run all examples."""
    print("🚀 IOIntelligenceChat Advanced Examples")
    print("=" * 60)

    # Check if API credentials are available
    if not os.getenv("IO_API_KEY") or not os.getenv("IO_API_URL"):
        print("⚠️  Please set IO_API_KEY and IO_API_URL in your .env file")
        return

    try:
        basic_chat_example()
        conversation_example()
        modern_chain_example()
        streaming_example()
        fallback_example()
        runtime_config_example()

        print("\n✅ All examples completed!")
        print("💡 Next steps:")
        print("   - Try configurable_alternatives() with multiple providers")
        print("   - Implement proper fallback chains with ChatOpenAI/ChatAnthropic")
        print("   - Add streaming support for real-time responses")

    except Exception as e:
        print(f"\n❌ Example execution failed: {e}")
        print("Make sure your IO Intelligence API is properly configured")


if __name__ == "__main__":
    main()
