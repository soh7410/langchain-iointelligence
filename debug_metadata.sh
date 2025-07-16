#!/bin/bash

echo "🔍 詳細な問題調査"
echo "=================="

# 1. ビルドされたパッケージのメタデータを確認
echo "📋 ビルドされたパッケージのメタデータ確認..."

if [ -f "dist/langchain_iointelligence-0.1.0-py3-none-any.whl" ]; then
    echo "🔍 Wheel ファイルのメタデータ:"
    python -c "
import zipfile
with zipfile.ZipFile('dist/langchain_iointelligence-0.1.0-py3-none-any.whl', 'r') as z:
    try:
        metadata = z.read('langchain_iointelligence-0.1.0.dist-info/METADATA').decode('utf-8')
        print('METADATA ファイル内容:')
        print('-' * 40)
        print(metadata)
    except Exception as e:
        print(f'METADATA読み取りエラー: {e}')
        print('ファイル一覧:')
        for file in z.namelist():
            print(f'  {file}')
"
else
    echo "❌ Wheel ファイルが見つかりません"
fi

# 2. PKG-INFO ファイルの確認
echo -e "\n📋 PKG-INFO ファイルの確認..."
if [ -f "langchain_iointelligence.egg-info/PKG-INFO" ]; then
    echo "PKG-INFO 内容:"
    cat langchain_iointelligence.egg-info/PKG-INFO
else
    echo "❌ PKG-INFO ファイルが見つかりません"
fi

# 3. pyproject.toml の構文確認
echo -e "\n📋 pyproject.toml の構文確認..."
python -c "
import toml
try:
    with open('pyproject.toml', 'r') as f:
        config = toml.load(f)
    print('✅ pyproject.toml 構文正常')
    print('プロジェクト名:', config.get('project', {}).get('name'))
    print('バージョン:', config.get('project', {}).get('version'))
except Exception as e:
    print(f'❌ pyproject.toml エラー: {e}')
"

echo -e "\n🔍 調査完了"
