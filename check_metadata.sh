#!/bin/bash

echo "🔍 メタデータファイル詳細確認"
echo "=========================="

# 1. Wheel ファイルの内容を詳細確認
echo "📦 Wheel ファイルの詳細確認..."
python -c "
import zipfile
import os

wheel_files = [f for f in os.listdir('dist/') if f.endswith('.whl')]
if wheel_files:
    wheel_file = wheel_files[0]
    print(f'Wheel ファイル: {wheel_file}')
    
    with zipfile.ZipFile(f'dist/{wheel_file}', 'r') as z:
        print('\n📁 ファイル一覧:')
        for file in sorted(z.namelist()):
            print(f'  {file}')
        
        print('\n📋 METADATA ファイル内容:')
        try:
            metadata = z.read('langchain_iointelligence-0.1.0.dist-info/METADATA').decode('utf-8')
            print('-' * 50)
            print(metadata)
            print('-' * 50)
        except Exception as e:
            print(f'❌ METADATA読み取りエラー: {e}')
            
        print('\n📋 WHEEL ファイル内容:')
        try:
            wheel_info = z.read('langchain_iointelligence-0.1.0.dist-info/WHEEL').decode('utf-8')
            print('-' * 30)
            print(wheel_info)
            print('-' * 30)
        except Exception as e:
            print(f'❌ WHEEL読み取りエラー: {e}')
else:
    print('❌ Wheel ファイルが見つかりません')
"

# 2. PKG-INFO ファイルの確認
echo -e "\n📋 PKG-INFO ファイルの確認..."
if [ -f "langchain_iointelligence.egg-info/PKG-INFO" ]; then
    echo "PKG-INFO 内容:"
    echo "=" * 40
    cat langchain_iointelligence.egg-info/PKG-INFO
    echo "=" * 40
else
    echo "❌ PKG-INFO ファイルが見つかりません"
fi

# 3. twine check の詳細出力
echo -e "\n🔍 twine check 詳細出力..."
python -m twine check dist/* --verbose

echo -e "\n🔍 確認完了"
