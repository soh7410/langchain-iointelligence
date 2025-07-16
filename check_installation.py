#!/usr/bin/env python3
"""Installation verification script."""

import sys
import os

def check_installation():
    """Check if langchain-iointelligence is properly installed."""
    print("🔍 Checking langchain-iointelligence installation...")
    
    try:
        # Import check
        from langchain_iointelligence import IOIntelligenceLLM
        print("✅ Package import successful")
        
        # Version check
        import langchain_iointelligence
        version = getattr(langchain_iointelligence, '__version__', 'unknown')
        print(f"📦 Version: {version}")
        
        # Environment check
        api_key = os.getenv('IO_API_KEY')
        api_url = os.getenv('IO_API_URL')
        
        if api_key and api_url:
            print("✅ Environment variables configured")
            
            # Basic initialization check
            try:
                llm = IOIntelligenceLLM()
                print("✅ LLM initialization successful")
                print(f"🔧 LLM type: {llm._llm_type}")
                print(f"🔧 Model: {llm.model}")
                print(f"🔧 Max tokens: {llm.max_tokens}")
                print(f"🔧 Temperature: {llm.temperature}")
                
            except Exception as e:
                print(f"❌ LLM initialization failed: {e}")
                
        else:
            print("⚠️  Environment variables not configured")
            print("   Please set IO_API_KEY and IO_API_URL")
            
        # Dependencies check
        print("\n📚 Checking dependencies...")
        dependencies = ['langchain', 'requests', 'dotenv']
        
        for dep in dependencies:
            try:
                __import__(dep.replace('-', '_'))
                print(f"✅ {dep}")
            except ImportError:
                print(f"❌ {dep} not found")
                
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("🔧 Try: pip install langchain-iointelligence")
        sys.exit(1)
    
    print("\n🎉 Installation check complete!")

if __name__ == "__main__":
    check_installation()
