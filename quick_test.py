"""Quick test script to verify the fixes."""

def main():
    print("🔍 Testing IOIntelligenceLLM fixes...")
    
    try:
        # Test import
        from langchain_iointelligence.llm import IOIntelligenceLLM
        print("✅ Import successful")
        
        # Test initialization
        llm = IOIntelligenceLLM(
            api_key='test_key',
            api_url='https://test.api.com/v1/completions'
        )
        print("✅ Initialization successful")
        
        # Test properties
        assert llm.io_api_key == 'test_key'
        assert llm.io_api_url == 'https://test.api.com/v1/completions'
        assert llm._llm_type == "io_intelligence"
        print("✅ All properties correct")
        
        print("🎉 All fixes working correctly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
