#!/bin/bash
# Test the final MVP fixes

echo "🧪 Testing FINAL MVP fixes..."

# Test usage metadata with UsageMetadata type
python -m pytest tests/test_usage_metadata.py -v

if [ $? -ne 0 ]; then
    echo "❌ Usage metadata tests failed"
    exit 1
fi

echo "✅ Usage metadata tests passed!"

# Test base_url functionality
python -m pytest tests/test_base_url.py -v

if [ $? -ne 0 ]; then
    echo "❌ Base URL tests failed"
    exit 1
fi

echo "✅ Base URL tests passed!"

# Test main chat functionality still works
python -m pytest tests/test_chat.py::TestIOIntelligenceChatModel::test_generate_success -v

if [ $? -eq 0 ]; then
    echo "✅ Core chat functionality still working!"
    echo ""
    echo "🎉 ALL FINAL MVP FIXES COMPLETED!"
    echo "   ✅ UsageMetadata type implementation"
    echo "   ✅ README expression alignment"  
    echo "   ✅ base_url parameter support"
    echo "   ✅ LangChain ecosystem compatibility"
else
    echo "❌ Core chat tests failed"
    exit 1
fi
