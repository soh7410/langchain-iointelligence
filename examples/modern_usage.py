"""Modern LangChain usage example."""

import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_iointelligence.llm import IOIntelligenceLLM

# Load environment variables
load_dotenv()

def main():
    """Modern LangChain usage example."""
    print("🚀 Modern langchain-iointelligence Example")
    print("=" * 50)
    
    # Initialize the LLM
    llm = IOIntelligenceLLM()
    
    # Modern approach - using invoke instead of __call__
    prompt = "Tell me a fun fact about koalas."
    
    print(f"📝 Prompt: {prompt}")
    print("\n🤖 Response (using invoke):")
    
    try:
        response = llm.invoke(prompt)
        print(response)
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure you have set IO_API_KEY and IO_API_URL in your .env file")
    
    print("\n" + "=" * 50)
    
    # Modern chain approach - using RunnableSequence
    print("🔗 Modern Chain Example")
    print("-" * 30)
    
    prompt_template = PromptTemplate.from_template(
        "Tell me a {adjective} joke about {topic}. Keep it clean and family-friendly."
    )
    
    # Modern way: prompt | llm
    chain = prompt_template | llm
    
    try:
        result = chain.invoke({"adjective": "funny", "topic": "robots"})
        print(f"🎭 Generated joke: {result}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
