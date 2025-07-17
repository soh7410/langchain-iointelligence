"""Advanced usage example with custom parameters."""


from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from langchain_iointelligence.llm import IOIntelligenceLLM

# Load environment variables
load_dotenv()


def main():
    """Advanced usage example with different configurations."""
    print("⚡ langchain-iointelligence Advanced Example")
    print("=" * 50)

    # Different configurations
    configs = [
        {
            "name": "Creative Writer",
            "model": "gpt-4",
            "max_tokens": 300,
            "temperature": 0.9,
            "prompt": "Write a creative short story about {topic} in exactly 2 paragraphs.",
        },
        {
            "name": "Technical Explainer",
            "model": "gpt-3.5-turbo",
            "max_tokens": 200,
            "temperature": 0.2,
            "prompt": "Explain {topic} in simple, technical terms suitable for beginners.",
        },
        {
            "name": "Conversational Assistant",
            "model": "default",
            "max_tokens": 150,
            "temperature": 0.5,
            "prompt": "Have a friendly conversation about {topic}. Ask one follow-up question.",
        },
    ]

    topics = ["artificial intelligence", "quantum computing", "sustainable energy"]

    for config in configs:
        print(f"\n🤖 {config['name']} Configuration:")
        print(f"   Model: {config['model']}")
        print(f"   Max Tokens: {config['max_tokens']}")
        print(f"   Temperature: {config['temperature']}")
        print("-" * 50)

        # Initialize LLM with specific config
        llm = IOIntelligenceLLM(
            model=config["model"],
            max_tokens=config["max_tokens"],
            temperature=config["temperature"],
        )

        # Create prompt template
        prompt_template = PromptTemplate.from_template(config["prompt"])

        # Create chain
        chain = LLMChain(llm=llm, prompt=prompt_template)

        # Test with first topic
        topic = topics[0]
        print(f"📝 Topic: {topic}")
        print("🤖 Response:")

        try:
            result = chain.run(topic=topic)
            print(result.strip())
        except Exception as e:
            print(f"❌ Error: {e}")

        print("\n" + "=" * 50)


def demonstrate_stop_words():
    """Demonstrate stop word functionality."""
    print("\n🛑 Stop Words Example")
    print("=" * 50)

    llm = IOIntelligenceLLM(max_tokens=500, temperature=0.5)

    prompt = "List the planets in our solar system: 1. Mercury, 2. Venus, 3."
    stop_words = ["5.", "Jupiter"]

    print(f"📝 Prompt: {prompt}")
    print(f"🛑 Stop words: {stop_words}")
    print("🤖 Response:")

    try:
        result = llm._call(prompt, stop=stop_words)
        print(result.strip())
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
    demonstrate_stop_words()
