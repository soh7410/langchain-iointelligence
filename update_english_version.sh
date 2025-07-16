#!/bin/bash

echo "🌐 English Version Update and Re-publish"
echo "========================================"

# 1. Update version number
echo "📈 Updating version to 0.1.1 (English version)..."
sed -i.bak 's/version="0.1.0"/version="0.1.1"/' setup.py

# 2. Update version in __init__.py
sed -i.bak 's/__version__ = "0.1.0"/__version__ = "0.1.1"/' langchain_iointelligence/__init__.py

# 3. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# 4. Build new version
echo "🏗️ Building new version..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ Build failed"
    exit 1
fi

# 5. Upload to TestPyPI
echo "🚀 Uploading to TestPyPI..."
python -m twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    echo "✅ Upload to TestPyPI successful!"
    echo ""
    echo "📦 New TestPyPI package:"
    echo "   pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ langchain-iointelligence==0.1.1"
    echo ""
    echo "🔗 TestPyPI URL:"
    echo "   https://test.pypi.org/project/langchain-iointelligence/0.1.1/"
    echo ""
    echo "🎯 Next steps:"
    echo "1. Test the new English version from TestPyPI"
    echo "2. If tests pass, publish to production PyPI"
    echo "3. Create GitHub repository with English documentation"
else
    echo "❌ Upload to TestPyPI failed"
fi

echo ""
echo "📋 Changes in v0.1.1:"
echo "- ✅ All documentation converted to English"
echo "- ✅ README.md fully translated"
echo "- ✅ Code comments in English"
echo "- ✅ Example files updated"
echo "- ✅ Ready for international distribution"
