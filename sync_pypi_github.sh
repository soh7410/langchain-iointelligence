#!/bin/bash

echo "🔄 Sync PyPI and GitHub"
echo "======================"

# 現在のバージョンを取得
CURRENT_VERSION=$(python setup.py --version)
echo "📋 Current version: $CURRENT_VERSION"

# Gitの状態確認
echo "📁 Git status:"
git status --porcelain

# 変更があるかチェック
if [ -n "$(git status --porcelain)" ]; then
    echo "📝 Changes detected. Committing..."
    
    echo "Commit message (or press Enter for default):"
    read COMMIT_MSG
    
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update langchain-iointelligence v$CURRENT_VERSION"
    fi
    
    git add .
    git commit -m "$COMMIT_MSG"
    
    echo "🚀 Pushing to GitHub..."
    git push origin main
    
    echo "✅ GitHub updated successfully!"
else
    echo "✅ No changes to commit"
fi

echo ""
echo "📦 PyPI Information:"
echo "- PyPI URL: https://pypi.org/project/langchain-iointelligence/"
echo "- Install: pip install langchain-iointelligence"
echo "- Version: $CURRENT_VERSION"

echo ""
echo "🐙 GitHub Information:"
echo "- Repository: https://github.com/YOUR_USERNAME/langchain-iointelligence"
echo "- Clone: git clone https://github.com/YOUR_USERNAME/langchain-iointelligence.git"

echo ""
echo "🚀 To publish new version:"
echo "1. Update version in setup.py"
echo "2. Run: python -m build"
echo "3. Run: python -m twine upload dist/*"
echo "4. Run: ./sync_pypi_github.sh"
