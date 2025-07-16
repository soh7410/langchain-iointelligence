#!/bin/bash

echo "🧪 TestPyPIからのインストール・動作テスト"
echo "========================================"

# 1. 新しい仮想環境でテスト
echo "📦 テスト用仮想環境を作成..."
python -m venv test_testpypi_env
source test_testpypi_env/bin/activate

echo "⬇️ TestPyPIからパッケージをインストール..."
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ langchain-iointelligence

if [ $? -eq 0 ]; then
    echo "✅ TestPyPIからのインストール成功！"
    
    echo "🧪 基本的な動作テスト..."
    python -c "
try:
    from langchain_iointelligence import IOIntelligenceLLM
    print('✅ インポート成功')
    
    # 基本的な初期化テスト
    llm = IOIntelligenceLLM(api_key='test', api_url='https://test.com')
    print('✅ 初期化成功')
    print(f'📦 LLM Type: {llm._llm_type}')
    print(f'📦 Model: {llm.model}')
    print(f'📦 Max Tokens: {llm.max_tokens}')
    print(f'📦 Temperature: {llm.temperature}')
    
    print('🎉 TestPyPIからのインストール・テストが完全に成功しました！')
    
except Exception as e:
    print(f'❌ テストエラー: {e}')
    import traceback
    traceback.print_exc()
"
else
    echo "❌ TestPyPIからのインストールに失敗しました"
fi

# 仮想環境を終了・削除
deactivate
rm -rf test_testpypi_env

echo -e "\n🚀 次のステップ:"
echo "1. TestPyPIでの動作確認が成功した場合、本番PyPIに公開できます"
echo "2. 本番PyPI公開コマンド: python -m twine upload dist/*"
echo "3. 本番PyPI URL: https://pypi.org/project/langchain-iointelligence/"
