#!/bin/bash
# Quick test of the fixed usage_metadata

echo "🧪 Testing fixed usage_metadata implementation..."

python -m pytest tests/test_usage_metadata.py -v

if [ $? -eq 0 ]; then
    echo "✅ usage_metadata tests passed!"
    
    # Test the main chat test
    python -m pytest tests/test_chat.py::TestIOIntelligenceChatModel::test_generate_success -v
    
    if [ $? -eq 0 ]; then
        echo "✅ Chat tests passed!"
        echo ""
        echo "🎉 All fixes working! Ready for push."
    else
        echo "❌ Chat tests failed"
        exit 1
    fi
else
    echo "❌ usage_metadata tests still failing"
    exit 1
fi
