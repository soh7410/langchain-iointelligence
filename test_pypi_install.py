#!/usr/bin/env python3
"""
Test installation from Test PyPI
Run this script after installing from Test PyPI to verify functionality.
"""

import sys
import subprocess

def test_installation():
    """Test that the package can be imported and basic functionality works."""
    print("🧪 Testing Test PyPI installation...")
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from langchain_iointelligence import IOIntelligenceChatModel, IOIntelligenceLLM
        from langchain_iointelligence import list_available_models, is_model_available
        print("✅ All imports successful!")
        
        # Test basic initialization
        print("🔧 Testing initialization...")
        chat = IOIntelligenceChatModel(
            api_key="test_key",
            api_url="https://test.example.com/v1/chat/completions"
        )
        assert chat.io_api_key == "test_key"
        assert chat._llm_type == "io_intelligence_chat"
        print("✅ Chat model initialization works!")
        
        llm = IOIntelligenceLLM(
            api_key="test_key", 
            api_url="https://test.example.com/v1/chat/completions"
        )
        assert llm.io_api_key == "test_key"
        assert llm._llm_type == "io_intelligence"
        print("✅ LLM initialization works!")
        
        # Test base_url functionality
        print("🌐 Testing base_url functionality...")
        chat_with_base = IOIntelligenceChatModel(
            api_key="test_key",
            base_url="https://api.example.com"
        )
        assert chat_with_base.io_api_url == "https://api.example.com/v1/chat/completions"
        print("✅ base_url functionality works!")
        
        # Test utility functions
        print("🛠️ Testing utility functions...")
        try:
            # These will not work without real API, but should not crash
            models = list_available_models()
            print("✅ list_available_models() callable")
        except Exception as e:
            if "API request failed" in str(e):
                print("✅ list_available_models() fails gracefully (expected without real API)")
            else:
                raise
        
        print("")
        print("🎉 All Test PyPI installation tests passed!")
        print("")
        print("📝 Package is working correctly from Test PyPI")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure you installed from Test PyPI:")
        print("   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence")
        return False
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test that all dependencies are available."""
    print("🔍 Testing dependencies...")
    
    required_packages = [
        "langchain_core",
        "requests", 
        "dotenv"
    ]
    
    for package in required_packages:
        try:
            if package == "dotenv":
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package} available")
        except ImportError:
            print(f"❌ {package} not available")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Test PyPI Installation Verification")
    print("=" * 50)
    
    # Test dependencies
    deps_ok = test_dependencies()
    
    print("")
    
    # Test installation
    install_ok = test_installation()
    
    print("=" * 50)
    if deps_ok and install_ok:
        print("🎉 Test PyPI installation verification PASSED!")
        print("")
        print("✅ Ready for production PyPI upload")
        return 0
    else:
        print("❌ Test PyPI installation verification FAILED!")
        return 1

if __name__ == "__main__":
    exit(main())
