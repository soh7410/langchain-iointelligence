#!/bin/bash
# Test the new flake8 configuration

echo "🔍 Testing new flake8 configuration (120 chars, relaxed rules)..."

# Test with the new settings
echo "Running flake8 on core library files..."
python -m flake8 langchain_iointelligence/ tests/ --count --statistics

if [ $? -eq 0 ]; then
    echo "✅ flake8 check passed with new 120-character limit!"
    echo ""
    echo "🧪 Running tests to ensure everything still works..."
    
    # Run tests
    python -m pytest tests/test_llm.py tests/test_chat.py -v
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 All checks passed! Ready for GitHub push."
        echo ""
        echo "📊 Configuration Summary:"
        echo "- Line length: 120 characters (was 79)"
        echo "- Examples excluded from linting"
        echo "- Common style warnings ignored"
        echo "- Core functionality preserved"
    else
        echo "❌ Tests failed - please check the code"
        exit 1
    fi
else
    echo "❌ flake8 still has issues - checking what's left..."
    python -m flake8 langchain_iointelligence/ tests/ --count --statistics --verbose
    exit 1
fi
