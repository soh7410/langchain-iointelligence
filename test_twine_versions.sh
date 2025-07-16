#!/bin/bash

echo "🔄 代替twineバージョンでテスト"
echo "============================"

# 1. 現在のtwineバージョン確認
echo "📋 現在のtwineバージョン:"
python -m twine --version

# 2. 古いバージョンのtwineをテスト
echo -e "\n📦 twine 3.8.0 でテスト..."
pip install twine==3.8.0

echo "🔍 古いtwineでパッケージ検証..."
python -m twine check dist/*

if [ $? -eq 0 ]; then
    echo "✅ 古いtwineで検証成功！"
else
    echo "❌ 古いtwineでも検証失敗"
fi

# 3. 最新版に戻す
echo -e "\n🔄 最新twineに戻す..."
pip install --upgrade twine

echo "🔍 確認完了"
