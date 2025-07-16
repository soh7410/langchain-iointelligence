#!/bin/bash

echo "🔍 TestPyPI アップロード問題の詳細確認"
echo "======================================"

# 1. 詳細なエラー情報を取得
echo "📋 詳細なエラー情報を取得中..."
python -m twine upload --repository testpypi dist/* --verbose

echo -e "\n" 

# 2. プロジェクト名の可用性確認
echo "🔍 TestPyPIでのプロジェクト名確認..."
curl -s "https://test.pypi.org/pypi/langchain-iointelligence/json" | head -20

if [ $? -eq 0 ]; then
    echo "⚠️  プロジェクト名 'langchain-iointelligence' は既に存在する可能性があります"
else
    echo "✅ プロジェクト名は利用可能のようです"
fi

echo -e "\n📝 次のステップ:"
echo "1. APIトークンを再確認"
echo "2. プロジェクト名を変更する場合の手順"
echo "3. 詳細なエラーログの確認"
