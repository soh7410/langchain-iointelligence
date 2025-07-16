#!/bin/bash

echo "🔄 プロジェクト名を一意な名前に変更"
echo "==============================="

# 現在のユーザー名またはランダムな識別子を追加
USERNAME=$(whoami)
TIMESTAMP=$(date +%Y%m%d)
NEW_NAME="langchain-iointelligence-${USERNAME}-${TIMESTAMP}"

echo "📝 新しいプロジェクト名: ${NEW_NAME}"

# setup.pyを更新
echo "🔧 setup.py を更新中..."
sed -i.bak "s/name=\"langchain-iointelligence\"/name=\"${NEW_NAME}\"/" setup.py

echo "🔧 __init__.py を更新中..."
# パッケージ名も更新（必要に応じて）

echo "🧹 古いビルドファイルを削除..."
rm -rf dist/ build/ *.egg-info/

echo "🏗️ 新しい名前でパッケージをビルド..."
python -m build

echo "🚀 TestPyPIにアップロード..."
python -m twine upload --repository testpypi dist/*

echo "✅ 更新完了！"
echo "📦 新しいパッケージ名: ${NEW_NAME}"
echo "🔗 TestPyPI URL: https://test.pypi.org/project/${NEW_NAME}/"
