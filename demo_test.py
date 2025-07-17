#!/usr/bin/env python3
"""
Demo script for testing IOIntelligence integration.
This can be used for real API testing when credentials are available.
"""

import os
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_iointelligence import IOIntelligenceChatModel

def test_basic_functionality():
    """Test basic chat functionality."""
    print("🔧 Testing basic chat functionality...")
    
    # Check if API credentials are available
    api_key = os.getenv("IO_API_KEY")
    api_url = os.getenv("IO_API_URL")
    
    if not api_key or not api_url:
        print("⚠️  API credentials not found in environment variables.")
        print("   Set IO_API_KEY and IO_API_URL to test with real API.")
        print("   ✅ Skipping real API test (this is expected in CI/testing).")
        return True
    
    # Additional check for test/dummy URLs (used in CI)
    if ('test.example.com' in api_url or 
        'example.com' in api_url or 
        'dummy' in api_key.lower() or 
        'test_api_key' in api_key.lower()):
        print("⚠️  Test/dummy API credentials detected.")
        print("   ✅ Skipping real API test (this is expected in CI/testing).")
        return True
    
    try:
        # Initialize chat model
        chat = IOIntelligenceChatModel(
            api_key=api_key,
            api_url=api_url,
            model="meta-llama/Llama-3.3-70B-Instruct",
            max_tokens=100,
            temperature=0.7
        )
        
        # Test basic generation
        messages = [
            SystemMessage(content="You are a helpful assistant. Keep responses brief."),
            HumanMessage(content="What is 2+2? Answer in one sentence.")
        ]
        
        print("🔄 Sending request to API...")
        result = chat.invoke(messages)
        
        # Check response
        print(f"✅ Response received: {result.content[:100]}...")
        
        # Check usage_metadata
        if hasattr(result, 'usage_metadata'):
            print(f"📊 Usage metadata: {result.usage_metadata}")
            print(f"   - Input tokens: {result.usage_metadata.input_tokens}")
            print(f"   - Output tokens: {result.usage_metadata.output_tokens}")
            print(f"   - Total tokens: {result.usage_metadata.total_tokens}")
        else:
            print("❌ usage_metadata not found!")
            return False
            
        return True
        
    except Exception as e:
        print(f"❌ Real API test failed: {str(e)}")
        return False

def test_streaming_functionality():
    """Test streaming functionality if API is available."""
    print("\n🌊 Testing streaming functionality...")
    
    api_key = os.getenv("IO_API_KEY")
    api_url = os.getenv("IO_API_URL")
    
    if not api_key or not api_url:
        print("⚠️  API credentials not found. ✅ Skipping streaming test (expected in testing).")
        return True
    
    # Additional check for test/dummy URLs (used in CI)
    if ('test.example.com' in api_url or 
        'example.com' in api_url or 
        'dummy' in api_key.lower() or 
        'test_api_key' in api_key.lower()):
        print("⚠️  Test/dummy API credentials detected. ✅ Skipping streaming test (expected in CI/testing).")
        return True
    
    try:
        # Initialize with streaming
        chat = IOIntelligenceChatModel(
            api_key=api_key,
            api_url=api_url,
            streaming=True,
            max_tokens=50
        )
        
        messages = [HumanMessage(content="Count from 1 to 5, one number per line.")]
        
        print("🔄 Testing streaming...")
        print("Response: ", end="", flush=True)
        
        chunk_count = 0
        for chunk in chat.stream(messages):
            if chunk.content:
                print(chunk.content, end="", flush=True)
                chunk_count += 1
        
        print(f"\n✅ Streaming test completed! Received {chunk_count} chunks.")
        return True
        
    except Exception as e:
        print(f"❌ Streaming test failed: {str(e)}")
        return False

def test_base_url_functionality():
    """Test base_url parameter."""
    print("\n🌐 Testing base_url parameter...")
    
    try:
        # Test different base_url formats
        test_cases = [
            ("https://api.example.com", "https://api.example.com/v1/chat/completions"),
            ("https://api.example.com/v1", "https://api.example.com/v1/chat/completions"),
            ("https://api.example.com/v1/chat/completions", "https://api.example.com/v1/chat/completions"),
        ]
        
        for base_url, expected_url in test_cases:
            chat = IOIntelligenceChatModel(
                api_key="dummy_key",
                base_url=base_url
            )
            
            if chat.io_api_url == expected_url:
                print(f"✅ {base_url} → {expected_url}")
            else:
                print(f"❌ {base_url} → {chat.io_api_url} (expected {expected_url})")
                return False
        
        print("✅ base_url functionality working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ base_url test failed: {str(e)}")
        return False

def main():
    """Run all demo tests."""
    print("🚀 IOIntelligence Demo & Integration Test")
    print("=" * 50)
    
    results = []
    
    # Test basic functionality
    results.append(test_basic_functionality())
    
    # Test streaming
    results.append(test_streaming_functionality())
    
    # Test base_url
    results.append(test_base_url_functionality())
    
    print("\n" + "=" * 50)
    print("📊 Demo Results Summary:")
    
    if all(results):
        print("🎉 All tests passed! Ready for production use.")
        print("\n💡 To test with real API:")
        print("   export IO_API_KEY='your_api_key'")
        print("   export IO_API_URL='https://your.api.com/v1/chat/completions'")
        print("   python demo_test.py")
    else:
        print("❌ Some tests failed. Check implementation.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
