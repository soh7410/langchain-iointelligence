#!/bin/bash

echo "🔍 公開後の確認スクリプト"
echo "=========================="

# 1. PyPIでのパッケージ確認
echo "📦 PyPIでのパッケージ確認..."
echo "🔗 PyPI: https://pypi.org/project/langchain-iointelligence/"
echo "🔗 TestPyPI: https://test.pypi.org/project/langchain-iointelligence/"

# 2. インストールテスト
echo -e "\n🧪 インストールテスト..."
echo "新しい環境でテストしますか？ [y/N]"
read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    # 新しい仮想環境でテスト
    echo "📦 新しい仮想環境でテスト..."
    python -m venv test_env
    source test_env/bin/activate
    
    echo "⬇️ パッケージのインストール..."
    pip install langchain-iointelligence
    
    echo "🧪 基本的な動作テスト..."
    python -c "
from langchain_iointelligence import IOIntelligenceLLM
print('✅ Import successful')
print('📦 Version:', IOIntelligenceLLM.__module__)
"
    
    deactivate
    rm -rf test_env
    
    echo "✅ テスト完了！"
fi

# 3. 使用統計の確認
echo -e "\n📊 使用統計の確認..."
echo "以下のサイトで統計を確認できます:"
echo "🔗 PyPI Stats: https://pypistats.org/packages/langchain-iointelligence"
echo "🔗 PePy: https://pepy.tech/project/langchain-iointelligence"

# 4. 次のステップ
echo -e "\n🚀 次のステップ:"
echo "1. GitHubリポジトリの作成・更新"
echo "2. ドキュメントの公開"
echo "3. コミュニティでの共有"
echo "4. フィードバックの収集"
echo "5. バージョンアップの計画"

echo -e "\n🎉 公開完了！"
