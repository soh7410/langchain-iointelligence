#!/bin/bash

echo "🔄 New Version with Unique Number"
echo "================================="

# 現在の時刻を使用して一意のバージョン番号を生成
TIMESTAMP=$(date +%H%M)
NEW_VERSION="0.1.1.${TIMESTAMP}"

echo "📈 Updating to version: ${NEW_VERSION}"

# setup.pyのバージョン更新
sed -i.bak "s/version=\"0.1.1\"/version=\"${NEW_VERSION}\"/" setup.py

# __init__.pyのバージョン更新
sed -i.bak "s/__version__ = \"0.1.1\"/__version__ = \"${NEW_VERSION}\"/" langchain_iointelligence/__init__.py

# 古いビルドファイルの削除
echo "🧹 Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/

# 新しいビルド
echo "🏗️ Building version ${NEW_VERSION}..."
python -m build

if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📦 Built files:"
    ls -la dist/
    
    echo ""
    echo "🚀 Ready to upload to TestPyPI"
    echo "Run: python -m twine upload --repository testpypi dist/*"
    echo ""
    echo "📋 New version details:"
    echo "Version: ${NEW_VERSION}"
    echo "Install command: pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ langchain-iointelligence==${NEW_VERSION}"
else
    echo "❌ Build failed"
fi
