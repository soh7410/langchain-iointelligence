#!/bin/bash
# Prepare for 0.1 release

echo "🏷️  Preparing 0.1 release tag..."

# 1. Run comprehensive tests
echo "🧪 Running comprehensive tests..."
chmod +x test_production_readiness.sh
./test_production_readiness.sh

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Cannot create release."
    exit 1
fi

# 2. Run demo test (offline tests)
echo "🎬 Running demo tests..."
python demo_test.py

if [ $? -ne 0 ]; then
    echo "❌ Demo tests failed! Cannot create release."
    exit 1
fi

echo "✅ All tests passed!"

# 3. Create release tag
echo "🏷️  Creating 0.1.0 release tag..."

# Check if tag already exists
if git tag -l | grep -q "v0.1.0"; then
    echo "⚠️  Tag v0.1.0 already exists. Use different version or delete existing tag."
    git tag -d v0.1.0 2>/dev/null
    git push origin :refs/tags/v0.1.0 2>/dev/null
    echo "   Deleted existing v0.1.0 tag."
fi

# Create annotated tag
git tag -a v0.1.0 -m "🎉 Release v0.1.0 - Production Ready LangChain Integration

✅ Complete LangChain ecosystem compatibility
✅ UsageMetadata standard implementation  
✅ OpenAI-compatible base_url parameter
✅ Comprehensive error handling
✅ Full test coverage and documentation

Features:
- Chat Model with message-based interface
- Text LLM with prompt-response interface  
- Token usage tracking (input/output/total)
- Streaming support (token-by-token)
- Automatic retries and error classification
- Model discovery utilities

Ready for production use! 🚀"

if [ $? -eq 0 ]; then
    echo "✅ Tag v0.1.0 created successfully!"
    
    # Push tag to GitHub
    echo "📤 Pushing tag to GitHub..."
    git push origin v0.1.0
    
    if [ $? -eq 0 ]; then
        echo "✅ Tag pushed to GitHub!"
        echo ""
        echo "🎉 Release v0.1.0 ready!"
        echo ""
        echo "📦 Next steps for PyPI release:"
        echo "   1. python -m build"
        echo "   2. python -m twine check dist/*"
        echo "   3. python -m twine upload dist/*"
        echo ""
        echo "🔗 GitHub release: https://github.com/your-username/langchain-iointelligence/releases/tag/v0.1.0"
    else
        echo "❌ Failed to push tag to GitHub"
        exit 1
    fi
else
    echo "❌ Failed to create tag"
    exit 1
fi
