#!/bin/bash

echo "🚀 PyPI公開手順スクリプト"
echo "==============================="

# 使用方法の説明
show_usage() {
    echo "使用方法:"
    echo "  ./publish_to_pypi.sh [test|prod]"
    echo ""
    echo "オプション:"
    echo "  test  - TestPyPIに公開（テスト用）"
    echo "  prod  - PyPIに公開（本番）"
    echo ""
    echo "例:"
    echo "  ./publish_to_pypi.sh test   # TestPyPIでテスト"
    echo "  ./publish_to_pypi.sh prod   # PyPIに本番公開"
}

# 引数チェック
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

TARGET=$1

# 1. 環境確認
echo "🔍 環境確認..."
if ! command -v python &> /dev/null; then
    echo "❌ Pythonが見つかりません"
    exit 1
fi

if ! python -m pip show build &> /dev/null; then
    echo "❌ buildパッケージが見つかりません。インストールしてください: pip install build"
    exit 1
fi

if ! python -m pip show twine &> /dev/null; then
    echo "❌ twineパッケージが見つかりません。インストールしてください: pip install twine"
    exit 1
fi

# 2. 古いビルドファイルの削除
echo "🧹 古いビルドファイルの削除..."
rm -rf dist/ build/ *.egg-info/

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

if [ $? -ne 0 ]; then
    echo "❌ パッケージの検証に失敗しました"
    exit 1
fi

# 5. アップロード
if [ "$TARGET" = "test" ]; then
    echo "🧪 TestPyPIにアップロード..."
    echo "TestPyPIの認証情報を入力してください:"
    python -m twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        echo "✅ TestPyPIへのアップロードが完了しました！"
        echo "🔗 確認: https://test.pypi.org/project/langchain-iointelligence/"
        echo "📦 テストインストール: pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence"
    else
        echo "❌ TestPyPIへのアップロードに失敗しました"
    fi
    
elif [ "$TARGET" = "prod" ]; then
    echo "🚀 PyPIにアップロード..."
    echo "⚠️  本番環境への公開を開始します。続行しますか？ [y/N]"
    read -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "PyPIの認証情報を入力してください:"
        python -m twine upload dist/*
        
        if [ $? -eq 0 ]; then
            echo "✅ PyPIへのアップロードが完了しました！"
            echo "🔗 確認: https://pypi.org/project/langchain-iointelligence/"
            echo "📦 インストール: pip install langchain-iointelligence"
        else
            echo "❌ PyPIへのアップロードに失敗しました"
        fi
    else
        echo "❌ 公開をキャンセルしました"
    fi
else
    echo "❌ 無効なオプションです"
    show_usage
    exit 1
fi

echo "🎉 完了！"
