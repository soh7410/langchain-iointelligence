#!/bin/bash

# 環境修復スクリプト
echo "🔧 環境の修復を開始します..."

# 1. 問題のあるパッケージをアンインストール
echo "📦 問題のあるパッケージを削除中..."
pip uninstall -y zstandard langsmith langchain-core langchain-text-splitters langchain

# 2. キャッシュをクリア
echo "🧹 pipキャッシュをクリア中..."
pip cache purge

# 3. 必要なパッケージを再インストール
echo "🔄 依存関係を再インストール中..."
pip install --force-reinstall --no-cache-dir zstandard
pip install --force-reinstall --no-cache-dir langsmith
pip install --force-reinstall --no-cache-dir langchain

# 4. 開発用パッケージをインストール
echo "🛠️ 開発用パッケージをインストール中..."
pip install --force-reinstall --no-cache-dir pytest>=8.3.4
pip install --force-reinstall --no-cache-dir pytest-cov>=2.0

# 5. プロジェクトを再インストール
echo "🏗️ プロジェクトを再インストール中..."
pip install -e .

echo "✅ 環境修復が完了しました！"
