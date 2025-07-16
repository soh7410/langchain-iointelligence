#!/bin/bash

echo "🧪 Testing English Version from TestPyPI"
echo "========================================"

# 1. Create test environment
echo "📦 Creating test environment..."
python -m venv test_english_env
source test_english_env/bin/activate

# 2. Install from TestPyPI
echo "⬇️ Installing langchain-iointelligence v0.1.1 from TestPyPI..."
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ langchain-iointelligence==0.1.1

if [ $? -eq 0 ]; then
    echo "✅ Installation successful!"
    
    # 3. Test import and basic functionality
    echo "🧪 Testing functionality..."
    python -c "
import sys
print('🐍 Python version:', sys.version)
print()

try:
    from langchain_iointelligence import IOIntelligenceLLM
    print('✅ Import successful')
    
    # Test initialization
    llm = IOIntelligenceLLM(api_key='test', api_url='https://test.com')
    print('✅ Initialization successful')
    print(f'📦 LLM Type: {llm._llm_type}')
    print(f'📦 Model: {llm.model}')
    print(f'📦 Max Tokens: {llm.max_tokens}')
    print(f'📦 Temperature: {llm.temperature}')
    
    # Test docstring (should be in English)
    print()
    print('📚 Class docstring:')
    print(f'   {IOIntelligenceLLM.__doc__}')
    
    print()
    print('🎉 English version testing successful!')
    
except Exception as e:
    print(f'❌ Test failed: {e}')
    import traceback
    traceback.print_exc()
"
else
    echo "❌ Installation failed"
fi

# 4. Cleanup
deactivate
rm -rf test_english_env

echo ""
echo "🚀 Next steps:"
echo "1. If tests pass, ready for production PyPI"
echo "2. Production publish command: python -m twine upload dist/*"
echo "3. After production publish: pip install langchain-iointelligence"
