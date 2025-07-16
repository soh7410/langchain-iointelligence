#!/bin/bash

echo "🔧 TestPyPI認証設定の確認・修正"
echo "=============================="

# 1. 現在の.pypirc確認
echo "📋 現在の .pypirc ファイルの確認..."
if [ -f ~/.pypirc ]; then
    echo "✅ .pypirc ファイルが存在します"
    echo "内容 (パスワード部分は隠されます):"
    cat ~/.pypirc | sed 's/password = .*/password = ***HIDDEN***/'
else
    echo "❌ .pypirc ファイルが見つかりません"
fi

echo -e "\n🔑 新しい .pypirc ファイルを作成しますか？ [y/N]"
read -n 1 -r
echo

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "TestPyPIのAPIトークンを入力してください (pypi- で始まる):"
    read -s TESTPYPI_TOKEN
    
    # バックアップを作成
    if [ -f ~/.pypirc ]; then
        cp ~/.pypirc ~/.pypirc.backup
        echo "📋 既存の .pypirc をバックアップしました"
    fi
    
    # 新しい .pypirc を作成
    cat > ~/.pypirc << EOF
[distutils]
index-servers =
    testpypi
    pypi

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = ${TESTPYPI_TOKEN}

[pypi]
repository = https://upload.pypi.org/legacy/
username = __token__
password = your_pypi_token_here
EOF
    
    echo "✅ 新しい .pypirc ファイルを作成しました"
    echo "🚀 TestPyPIへのアップロードを試してください:"
    echo "   python -m twine upload --repository testpypi dist/*"
else
    echo "❌ .pypirc の作成をスキップしました"
fi

echo -e "\n💡 手動でAPIトークンを入力する場合:"
echo "   python -m twine upload --repository testpypi dist/* --username __token__"
