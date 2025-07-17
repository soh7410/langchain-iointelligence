#!/bin/bash
# Clean up temporary files before GitHub push

echo "🧹 Cleaning up temporary development files..."

# Remove temporary development scripts
rm -f check_syntax.py
rm -f check_flake8.py
rm -f final_verification.py
rm -f fix_installation.py
rm -f fix_lint_errors.py
rm -f run_chat_tests.py
rm -f run_direct_tests.py
rm -f simple_test.py
rm -f test_complete_solution.py
rm -f test_refactoring.py
rm -f verify_basic.py
rm -f quick_fix_test.py
rm -f quick_test.py

# Remove temporary shell scripts
rm -f test_critical_fixes.sh
rm -f test_demo_fix.sh
rm -f test_final_mvp.sh
rm -f test_new_lint_config.sh
rm -f test_production_readiness.sh
rm -f lint_and_test.sh
rm -f delete_pytest_ini
rm -f emergency_test.sh
rm -f fix_imports.sh
rm -f format_code.sh

# Remove temporary documentation
rm -f COMMIT_MESSAGE.md
rm -f LINT_OPTIONS.md
rm -f PUSH_CHECKLIST.md

# Remove alternative configurations
rm -f .flake8.ultra-relaxed

echo "✅ Temporary files cleaned up!"

# Show remaining important files
echo ""
echo "📋 Remaining development tools:"
ls -la demo_test.py prepare_release.sh push_to_github.sh 2>/dev/null || echo "   Development scripts ready"

echo ""
echo "🚀 Ready for clean GitHub push!"
