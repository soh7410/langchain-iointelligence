#!/bin/bash

echo "🔍 パッケージの最終確認を開始..."

# 1. 必要なファイルの存在確認
echo "📁 必要なファイルの確認..."
required_files=(
    "setup.py"
    "pyproject.toml"
    "README.md"
    "LICENSE"
    "langchain_iointelligence/__init__.py"
    "langchain_iointelligence/llm.py"
    ".env.example"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - 見つかりません"
    fi
done

# 2. パッケージのビルドテスト
echo -e "\n🏗️ パッケージのビルドテスト..."
python -m build --sdist --wheel . || echo "❌ ビルドに失敗しました"

# 3. パッケージの内容確認
echo -e "\n📦 ビルドされたパッケージの確認..."
ls -la dist/

# 4. パッケージの検証
echo -e "\n🔍 パッケージの検証..."
python -m twine check dist/*

echo -e "\n✅ 最終確認完了！"
