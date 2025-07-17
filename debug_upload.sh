#!/bin/bash
# Debug Test PyPI upload with verbose output

echo "🔍 Debugging Test PyPI upload..."

# Check if we have distributions
if [ ! -d "dist/" ] || [ -z "$(ls -A dist/)" ]; then
    echo "❌ No distributions found in dist/"
    echo "Run the build process first."
    exit 1
fi

echo "📦 Found distributions:"
ls -la dist/

# Try upload with verbose output to see the exact error
echo ""
echo "🚀 Attempting upload with verbose output..."
python -m twine upload --repository testpypi dist/* --verbose

if [ $? -eq 0 ]; then
    echo "✅ Upload successful!"
else
    echo ""
    echo "❌ Upload failed. Common solutions:"
    echo ""
    echo "1. 🏷️ **Package name conflict**:"
    echo "   - Try changing package name in pyproject.toml"
    echo "   - Example: 'langchain-iointelligence' → 'langchain-iointelligence-test'"
    echo ""
    echo "2. 🔄 **Version already exists**:"
    echo "   - Bump version in pyproject.toml"
    echo "   - Example: '0.1.0' → '0.1.1'"
    echo ""
    echo "3. 🔑 **Authentication issues**:"
    echo "   - Username must be '__token__'"
    echo "   - Password must be your API token (starts with 'pypi-')"
    echo ""
    echo "4. 📋 **Package metadata issues**:"
    echo "   - Check pyproject.toml for required fields"
    echo "   - Ensure README.md exists and is referenced correctly"
    echo ""
    echo "Run this script again to retry with verbose output."
fi
