#!/bin/bash

echo "🔧 最終修正版パッケージテスト"
echo "============================"

# 1. 完全なクリーンアップ
echo "🧹 完全なクリーンアップ..."
rm -rf dist/ build/ *.egg-info/ __pycache__/ */__pycache__/

# 2. setup.py直接テスト
echo "📋 setup.py直接テスト..."
python setup.py --name
python setup.py --version

# 3. パッケージのビルド
echo "🏗️ パッケージのビルド..."
python -m build

if [ $? -ne 0 ]; then
    echo "❌ ビルドに失敗しました"
    exit 1
fi

# 4. パッケージの検証
echo "🔍 パッケージの検証..."
python -m twine check dist/*

if [ $? -eq 0 ]; then
    echo "✅ パッケージの検証に成功しました！"
    echo "📦 ビルドされたファイル:"
    ls -la dist/
    
    # 5. 詳細なメタデータ確認
    echo "🔍 詳細なメタデータ確認..."
    python -c "
import zipfile
import os

wheel_files = [f for f in os.listdir('dist/') if f.endswith('.whl')]
if wheel_files:
    wheel_file = wheel_files[0]
    with zipfile.ZipFile(f'dist/{wheel_file}', 'r') as z:
        try:
            metadata = z.read('langchain_iointelligence-0.1.0.dist-info/METADATA').decode('utf-8')
            print('✅ METADATA ファイル読み取り成功')
            lines = metadata.split('\n')
            for line in lines[:15]:  # 最初の15行を表示
                print(f'  {line}')
        except Exception as e:
            print(f'❌ METADATA読み取りエラー: {e}')
"
    
    echo "✅ 最終テスト完了！公開準備完了です！"
else
    echo "❌ パッケージの検証に失敗しました"
    exit 1
fi
