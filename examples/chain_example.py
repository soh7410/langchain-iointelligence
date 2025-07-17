"""LangChain chain integration example."""

import os
from dotenv import load_dotenv
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain_iointelligence.llm import IOIntelligenceLLM

# Load environment variables
load_dotenv()

def main():
    """LangChain chain integration example."""
    print("🔗 langchain-iointelligence Chain Example")
    print("=" * 50)
    
    # Initialize the LLM
    llm = IOIntelligenceLLM(
        model="meta-llama/Llama-3.3-70B-Instruct",
        max_tokens=200,
        temperature=0.7
    )
    
    # Create a prompt template
    prompt_template = PromptTemplate.from_template(
        "Tell me a {adjective} joke about {topic}. Keep it clean and family-friendly."
    )
    
    # Create a chain
    chain = LLMChain(llm=llm, prompt=prompt_template)
    
    # Test data
    test_cases = [
        {"adjective": "funny", "topic": "robots"},
        {"adjective": "clever", "topic": "programming"},
        {"adjective": "silly", "topic": "cats"},
    ]
    
    print("🎭 Generated Jokes:")
    print("-" * 30)
    
    for i, case in enumerate(test_cases, 1):
        try:
            result = chain.run(**case)
            print(f"{i}. {case['adjective'].title()} {case['topic']} joke:")
            print(f"   {result.strip()}")
            print()
        except Exception as e:
            print(f"❌ Error for case {i}: {e}")
            print()

if __name__ == "__main__":
    main()
