#!/bin/bash
# Simple Test PyPI upload with better error handling

echo "🚀 Simple Test PyPI upload..."

# Check distributions exist
if [ ! -f "dist/"*.whl ] || [ ! -f "dist/"*.tar.gz ]; then
    echo "❌ No distributions found. Run build first:"
    echo "   python -m build"
    exit 1
fi

echo "📦 Found distributions:"
ls -1 dist/

echo ""
echo "🔑 Authentication info:"
echo "   Username: __token__"
echo "   Password: [Your Test PyPI API token]"
echo ""
echo "💡 Get API token from: https://test.pypi.org/manage/account/token/"
echo ""

# Simple upload command
python -m twine upload --repository testpypi dist/* --verbose

upload_status=$?

if [ $upload_status -eq 0 ]; then
    echo ""
    echo "🎉 Upload successful!"
    echo ""
    echo "📦 Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence-testpkg"
    echo ""
    echo "🔗 View package:"
    echo "   https://test.pypi.org/project/langchain-iointelligence-testpkg/"
else
    echo ""
    echo "❌ Upload failed (exit code: $upload_status)"
    echo ""
    echo "🔧 Try these solutions:"
    echo ""
    echo "1. **Check credentials**:"
    echo "   - Username must be exactly: __token__"
    echo "   - Password must be your full API token"
    echo ""
    echo "2. **Package name conflict**:"
    echo "   - Run: ./fix_testpypi.sh"
    echo "   - This creates a unique test package name"
    echo ""
    echo "3. **Version conflict**:"
    echo "   - Edit pyproject.toml and change version (0.1.0 → 0.1.1)"
    echo "   - Rebuild: python -m build"
    echo ""
    echo "4. **Try manual upload**:"
    echo "   python -m twine upload --repository testpypi dist/*.whl"
fi
