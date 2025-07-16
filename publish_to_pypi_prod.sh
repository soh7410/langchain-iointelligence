#!/bin/bash

echo "🚀 本番PyPIへの公開"
echo "==================="

echo "⚠️  注意: 本番PyPIへの公開は取り消しできません！"
echo "TestPyPIでのテストが完了していることを確認してください。"
echo ""
echo "続行しますか？ [y/N]"
read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📋 本番PyPIのAPIトークンが必要です。"
    echo "🔗 取得先: https://pypi.org/manage/account/token/"
    echo ""
    
    echo "🚀 本番PyPIにアップロード中..."
    python -m twine upload dist/*
    
    if [ $? -eq 0 ]; then
        echo "🎉 本番PyPIへの公開が成功しました！"
        echo ""
        echo "📦 インストール: pip install langchain-iointelligence"
        echo "🔗 PyPIページ: https://pypi.org/project/langchain-iointelligence/"
        echo ""
        echo "🎯 次のステップ:"
        echo "1. GitHubリポジトリの作成・更新"
        echo "2. ドキュメントの公開"
        echo "3. コミュニティでの共有"
        echo "4. README.mdのバッジ更新"
    else
        echo "❌ 本番PyPIへの公開に失敗しました"
        echo "💡 Troubleshooting:"
        echo "- PyPI APIトークンを確認"
        echo "- プロジェクト名の競合確認"
        echo "- 詳細エラー: python -m twine upload dist/* --verbose"
    fi
else
    echo "❌ 公開をキャンセルしました"
    echo "💡 TestPyPIでさらにテストを行うか、設定を確認してから再度実行してください"
fi
