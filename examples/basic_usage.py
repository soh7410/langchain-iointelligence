"""Basic usage example for langchain-iointelligence."""

import os
from dotenv import load_dotenv
from langchain_iointelligence.llm import IOIntelligenceLLM

# Load environment variables
load_dotenv()

def main():
    """Basic usage example."""
    print("🚀 langchain-iointelligence Basic Example")
    print("=" * 50)
    
    # Initialize the LLM
    llm = IOIntelligenceLLM()
    
    # Simple prompt
    prompt = "Tell me a fun fact about koalas."
    
    print(f"📝 Prompt: {prompt}")
    print("\n🤖 Response:")
    
    try:
        response = llm.invoke(prompt)
        print(response)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have set IO_API_KEY and IO_API_URL in your .env file")

if __name__ == "__main__":
    main()
