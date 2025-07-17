#!/bin/bash
# Upload to Test PyPI

echo "📦 Preparing Test PyPI upload..."

# 1. Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf build/
rm -rf *.egg-info/

# 2. Install build tools if needed
echo "🔧 Installing/upgrading build tools..."
pip install --upgrade build twine

# 3. Run tests to ensure everything works
echo "🧪 Running final tests..."
python -m pytest tests/ -v --tb=short

if [ $? -ne 0 ]; then
    echo "❌ Tests failed! Cannot upload to PyPI."
    exit 1
fi

echo "✅ All tests passed!"

# 4. Build the package
echo "📦 Building package..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

echo "✅ Package built successfully!"

# 5. Check the built package
echo "🔍 Checking package..."
python -m twine check dist/*

if [ $? -ne 0 ]; then
    echo "❌ Package check failed!"
    exit 1
fi

echo "✅ Package check passed!"

# 6. Show what will be uploaded
echo "📋 Package contents:"
ls -la dist/

echo ""
echo "📄 Package info:"
python -c "
import os
for file in os.listdir('dist'):
    if file.endswith('.whl') or file.endswith('.tar.gz'):
        print(f'  - {file}')
        if file.endswith('.tar.gz'):
            size = os.path.getsize(f'dist/{file}')
            print(f'    Size: {size:,} bytes')
"

# 7. Upload to Test PyPI
echo ""
echo "🚀 Uploading to Test PyPI..."
echo "⚠️  You will need your Test PyPI API token."
echo "   Get it from: https://test.pypi.org/manage/account/token/"
echo ""

python -m twine upload --repository testpypi dist/*

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Successfully uploaded to Test PyPI!"
    echo ""
    echo "📦 Test installation:"
    echo "   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence"
    echo ""
    echo "🔗 View on Test PyPI:"
    echo "   https://test.pypi.org/project/langchain-iointelligence/"
    echo ""
    echo "✅ Next steps:"
    echo "   1. Test install from Test PyPI"
    echo "   2. Verify functionality"
    echo "   3. Upload to production PyPI when ready"
else
    echo "❌ Upload to Test PyPI failed!"
    echo ""
    echo "💡 Common issues:"
    echo "   - Need to create account at https://test.pypi.org/"
    echo "   - Need API token from https://test.pypi.org/manage/account/token/"
    echo "   - Package version might already exist"
    exit 1
fi
