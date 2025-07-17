#!/bin/bash
# Test the critical fixes

echo "🧪 Testing usage_metadata fixes..."

# Test the specific usage metadata functionality
python -m pytest tests/test_usage_metadata.py -v

if [ $? -eq 0 ]; then
    echo "✅ usage_metadata tests passed!"
    
    # Test the chat model with updated assertions
    python -m pytest tests/test_chat.py::TestIOIntelligenceChatModel::test_generate_success -v
    
    if [ $? -eq 0 ]; then
        echo "✅ Chat model tests passed!"
        echo ""
        echo "🎉 All critical fixes working!"
    else
        echo "❌ Chat model tests failed"
        exit 1
    fi
else
    echo "❌ usage_metadata tests failed"
    exit 1
fi
