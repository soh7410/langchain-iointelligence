#!/bin/bash

echo "🔍 TestPyPI アップロード問題の詳細分析"
echo "======================================"

# 1. 現在のTestPyPIの状況確認
echo "📋 TestPyPIの現在の状況確認..."
curl -s "https://test.pypi.org/pypi/langchain-iointelligence/json" | python -m json.tool | grep -A 3 -B 3 "version"

# 2. ビルドされたファイルの確認
echo -e "\n📦 ビルドされたファイルの確認..."
ls -la dist/

# 3. 詳細なアップロード試行
echo -e "\n🔧 詳細なアップロード試行..."
echo "TestPyPI APIトークンを再入力してください:"
python -m twine upload --repository testpypi dist/* --verbose

echo -e "\n💡 Troubleshooting tips:"
echo "1. APIトークンが 'pypi-' で始まっていることを確認"
echo "2. TestPyPIの正しいトークンを使用していることを確認"
echo "3. 同じバージョンを再アップロードしようとしていないか確認"
