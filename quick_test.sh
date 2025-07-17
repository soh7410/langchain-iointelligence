#!/bin/bash
# Quick flake8 test

echo "🔍 Testing flake8 configuration..."

python -m flake8 langchain_iointelligence/ tests/ --count --statistics

if [ $? -eq 0 ]; then
    echo "✅ flake8 check passed!"
    echo ""
    echo "🧪 Running quick test..."
    python -m pytest tests/test_basic.py tests/test_chat.py::TestIOIntelligenceChatModel::test_llm_type -v
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "🎉 Ready for push!"
    else
        echo "❌ Tests failed"
        exit 1
    fi
else
    echo "❌ flake8 check failed"
    exit 1
fi
