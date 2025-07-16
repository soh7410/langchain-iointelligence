#!/bin/bash

echo "🔧 修正版パッケージテスト"
echo "========================"

# 1. 古いビルドファイルの削除
echo "🧹 古いビルドファイルの削除..."
rm -rf dist/ build/ *.egg-info/

# 2. パッケージのビルド
echo "🏗️ パッケージのビルド..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ ビルドに失敗しました"
    exit 1
fi

# 3. パッケージの検証
echo "🔍 パッケージの検証..."
python -m twine check dist/*

if [ $? -eq 0 ]; then
    echo "✅ パッケージの検証に成功しました！"
    echo "📦 ビルドされたファイル:"
    ls -la dist/
else
    echo "❌ パッケージの検証に失敗しました"
    exit 1
fi

# 4. メタデータの確認
echo "🔍 メタデータの確認..."
python -c "
import zipfile
import os

wheel_file = [f for f in os.listdir('dist/') if f.endswith('.whl')][0]
with zipfile.ZipFile(f'dist/{wheel_file}', 'r') as z:
    metadata = z.read('langchain_iointelligence-0.1.0.dist-info/METADATA').decode('utf-8')
    print('📋 メタデータ:')
    print(metadata[:500] + '...' if len(metadata) > 500 else metadata)
"

echo "✅ 修正版テスト完了！"
