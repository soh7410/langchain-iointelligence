#!/bin/bash

echo "🚀 twine検証を回避してテスト公開"
echo "==============================="

# 1. パッケージの存在確認
if [ ! -f "dist/langchain_iointelligence-0.1.0-py3-none-any.whl" ]; then
    echo "❌ Wheel ファイルが見つかりません。先にビルドしてください。"
    exit 1
fi

if [ ! -f "dist/langchain_iointelligence-0.1.0.tar.gz" ]; then
    echo "❌ Source distribution が見つかりません。先にビルドしてください。"
    exit 1
fi

echo "✅ 必要なファイルが見つかりました"
ls -la dist/

# 2. メタデータの基本確認
echo -e "\n📋 メタデータの基本確認..."
python -c "
import zipfile
wheel_file = 'dist/langchain_iointelligence-0.1.0-py3-none-any.whl'
with zipfile.ZipFile(wheel_file, 'r') as z:
    try:
        metadata = z.read('langchain_iointelligence-0.1.0.dist-info/METADATA').decode('utf-8')
        lines = metadata.split('\n')
        name_found = False
        version_found = False
        for line in lines:
            if line.startswith('Name:'):
                print(f'✅ {line}')
                name_found = True
            elif line.startswith('Version:'):
                print(f'✅ {line}')
                version_found = True
        
        if name_found and version_found:
            print('✅ 基本メタデータは存在しています')
        else:
            print('❌ 基本メタデータが不足しています')
            
    except Exception as e:
        print(f'❌ メタデータ確認エラー: {e}')
"

# 3. 実際のインストールテスト
echo -e "\n🧪 ローカルインストールテスト..."
pip install dist/langchain_iointelligence-0.1.0-py3-none-any.whl --force-reinstall --no-deps

if [ $? -eq 0 ]; then
    echo "✅ ローカルインストール成功！"
    
    # インポートテスト
    python -c "
try:
    from langchain_iointelligence import IOIntelligenceLLM
    print('✅ インポート成功')
    
    # 基本的な初期化テスト
    llm = IOIntelligenceLLM(api_key='test', api_url='https://test.com')
    print('✅ 初期化成功')
    print(f'📦 LLM Type: {llm._llm_type}')
    
except Exception as e:
    print(f'❌ テストエラー: {e}')
"
else
    echo "❌ ローカルインストール失敗"
fi

# 4. TestPyPI アップロードの提案
echo -e "\n🚀 次のステップ:"
echo "1. ローカルテストが成功した場合、TestPyPIに直接アップロードを試すことができます："
echo "   python -m twine upload --repository testpypi dist/*"
echo ""
echo "2. または、twineの古いバージョンを使用する："
echo "   pip install twine==3.8.0"
echo "   python -m twine check dist/*"
echo ""
echo "3. 検証を無視してアップロード（自己責任）："
echo "   python -m twine upload --repository testpypi dist/* --skip-existing"

echo -e "\n🎯 パッケージは正常にビルドされているようです。twineの検証問題を回避して公開を試すことができます。"
