#!/bin/bash
# Lint check and test script for modified files

echo "🔍 Running flake8 check on test_llm.py..."

# Check for flake8 compliance
python -m flake8 tests/test_llm.py --max-line-length=79 --ignore=E203,W503

if [ $? -eq 0 ]; then
    echo "✅ flake8 check passed!"
else
    echo "❌ flake8 check failed!"
    exit 1
fi

echo ""
echo "🧪 Running tests to ensure functionality..."

# Run the LLM tests
python -m pytest tests/test_llm.py -v

if [ $? -eq 0 ]; then
    echo "✅ Tests passed!"
else
    echo "❌ Tests failed!"
    exit 1
fi

echo ""
echo "🎉 All checks passed! Ready for GitHub push."
