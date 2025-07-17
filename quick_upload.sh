#!/bin/bash
# Quick rebuild and upload v0.1.1

echo "🔄 Rebuilding and uploading v0.1.1..."

# Check version was updated
version=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
echo "📝 Package version: $version"

if [ "$version" = "0.1.0" ]; then
    echo "❌ Version still 0.1.0! Please update pyproject.toml first."
    exit 1
fi

# Clean and rebuild
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

echo "📦 Building package..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Build successful!"
echo ""
echo "📋 Package contents:"
ls -la dist/

echo ""
echo "🔍 Checking package..."
python -m twine check dist/*

if [ $? -ne 0 ]; then
    echo "❌ Package check failed!"
    exit 1
fi

echo "✅ Package check passed!"
echo ""
echo "🚀 Uploading to Test PyPI..."
python -m twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Successfully uploaded v$version to Test PyPI!"
    echo ""
    echo "🔗 View package: https://test.pypi.org/project/langchain-iointelligence/"
    echo ""
    echo "📦 Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence"
    echo ""
    echo "✅ Update complete!"
else
    echo "❌ Upload failed!"
    exit 1
fi
