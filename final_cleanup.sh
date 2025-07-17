#!/bin/bash
# Git push前の完全クリーンアップスクリプト

echo "🧹 langchain-iointelligence Git Push前クリーンアップ"
echo "=================================================="

# 1. 不要ファイルの削除
echo "1️⃣ 不要ファイルの削除"
echo "------------------"

# 不明なファイル
if [ -f "=2.0" ]; then
    rm "=2.0"
    echo "   ✅ =2.0 削除"
fi

if [ -f "=8.3.4" ]; then
    rm "=8.3.4"
    echo "   ✅ =8.3.4 削除"
fi

# バックアップファイル
if [ -f "setup.py.bak" ]; then
    rm "setup.py.bak"
    echo "   ✅ setup.py.bak 削除"
fi

if [ -f "langchain_iointelligence/__init__.py.bak" ]; then
    rm "langchain_iointelligence/__init__.py.bak"
    echo "   ✅ __init__.py.bak 削除"
fi

# 一時的な開発用スクリプト
TEMP_FILES=(
    "analyze_files.py"
    "run_tests_guide.py" 
    "diagnose_issues.py"
    "test_results_guide.py"
    "check_test_environment.sh"
    "fix_pytest_environment.sh"
    "cleanup_for_git.sh"
    "analyze_for_git.py"
)

for file in "${TEMP_FILES[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "   ✅ $file 削除"
    fi
done

# 多数のシェルスクリプト（必要最小限を残す）
SHELL_SCRIPTS_TO_DELETE=(
    "analyze_project_structure.sh"
    "check_installation.py"
    "check_metadata.sh"
    "create_unique_version.sh"
    "debug_metadata.sh"
    "debug_testpypi_upload.sh"
    "debug_upload.sh"
    "final_test.sh"
    "fix_environment.sh"
    "fix_pypirc.sh"
    "post_publish_check.sh"
    "pre_publish_check.sh"
    "publish_to_pypi.sh"
    "publish_to_pypi_prod.sh"
    "quick_test.py"
    "rename_and_upload.sh"
    "setup_github_repo.sh"
    "setup_pypirc.sh"
    "sync_pypi_github.sh"
    "test_english_version.sh"
    "test_fixed_package.sh"
    "test_from_testpypi.sh"
    "test_twine_versions.sh"
    "test_without_twine_check.sh"
    "update_english_version.sh"
)

for file in "${SHELL_SCRIPTS_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        rm "$file"
        echo "   ✅ $file 削除"
    fi
done

# 2. ビルド成果物の削除
echo -e "\n2️⃣ ビルド成果物の削除"
echo "--------------------"

if [ -d "dist" ]; then
    rm -rf dist/
    echo "   ✅ dist/ 削除"
fi

if [ -d "build" ]; then
    rm -rf build/
    echo "   ✅ build/ 削除"
fi

if [ -d "langchain_iointelligence.egg-info" ]; then
    rm -rf langchain_iointelligence.egg-info/
    echo "   ✅ .egg-info/ 削除"
fi

# 3. Pythonキャッシュの削除
echo -e "\n3️⃣ Pythonキャッシュの削除"
echo "----------------------"

find . -name "*.pyc" -delete 2>/dev/null && echo "   ✅ .pyc ファイル削除"
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null && echo "   ✅ __pycache__ ディレクトリ削除"

# 4. 一時ディレクトリの削除
echo -e "\n4️⃣ 一時ディレクトリの削除"
echo "--------------------"

if [ -d "test_env" ]; then
    rm -rf test_env/
    echo "   ✅ test_env/ 削除"
fi

if [ -d ".pytest_cache" ]; then
    rm -rf .pytest_cache/
    echo "   ✅ .pytest_cache/ 削除"
fi

# 5. 残ったファイルの確認
echo -e "\n5️⃣ 残存ファイル確認"
echo "----------------"

echo "📁 保持される重要ファイル:"
ESSENTIAL_FILES=(
    "langchain_iointelligence/__init__.py"
    "langchain_iointelligence/llm.py"
    "langchain_iointelligence/chat.py"
    "langchain_iointelligence/exceptions.py"
    "langchain_iointelligence/http_client.py"
    "langchain_iointelligence/streaming.py"
    "langchain_iointelligence/utils.py"
    "tests/test_llm.py"
    "tests/test_chat.py"
    "examples/chat_examples.py"
    "README.md"
    "setup.py"
    ".gitignore"
)

for file in "${ESSENTIAL_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    else
        echo "   ❌ $file (見つかりません)"
    fi
done

echo -e "\n📝 保持される開発用ファイル:"
DEV_FILES=(
    "test_refactoring.py"
    "final_verification.py" 
    "run_direct_tests.py"
    "test_complete_solution.py"
)

for file in "${DEV_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✅ $file"
    fi
done

echo -e "\n=================================================="
echo "✨ クリーンアップ完了！"
echo "=================================================="
echo "📦 Git Push手順:"
echo "   1. git add ."
echo "   2. git status  # 状態確認"
echo "   3. git commit -m \"feat: Complete ChatGPT API compatibility\""  
echo "   4. git push origin main"
echo ""
echo "🎯 準備完了機能:"
echo "   ✅ ChatGPT完全互換API"
echo "   ✅ 真のストリーミング対応"  
echo "   ✅ 詳細エラー分類"
echo "   ✅ モデル発見機能"
echo "   ✅ プロダクション信頼性"
echo ""
