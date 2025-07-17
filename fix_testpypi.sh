#!/bin/bash
# Fix package for Test PyPI upload

echo "🔧 Fixing package for Test PyPI upload..."

# Create a backup of original pyproject.toml
cp pyproject.toml pyproject.toml.backup

# Create test version with unique name
cat > pyproject.toml << 'EOF'
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "langchain-iointelligence-testpkg"
version = "0.1.0"
description = "LangChain integration for io Intelligence LLM API with OpenAI compatibility (Test Package)"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "io Intelligence", email = "support@intelligence.io"}
]
keywords = [
    "langchain", 
    "llm", 
    "ai", 
    "openai", 
    "chat", 
    "language-model",
    "io-intelligence"
]
classifiers = [
    "Development Status :: 4 - Beta",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering :: Artificial Intelligence",
    "Topic :: Software Development :: Libraries :: Python Modules",
]
dependencies = [
    "langchain-core>=0.1.0",
    "requests>=2.25.0",
    "python-dotenv>=0.19.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "flake8>=5.0.0",
    "black>=22.0.0",
    "isort>=5.10.0",
    "mypy>=0.991",
]

[project.urls]
Homepage = "https://github.com/soh7410/langchain-iointelligence"
Repository = "https://github.com/soh7410/langchain-iointelligence"
Documentation = "https://github.com/soh7410/langchain-iointelligence#readme"
"Bug Tracker" = "https://github.com/soh7410/langchain-iointelligence/issues"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
python_classes = "Test*"
python_functions = "test_*"
addopts = [
    "--strict-markers",
    "--strict-config", 
    "--cov-report=term-missing",
    "-ra",
    "--tb=short"
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests"
]
filterwarnings = [
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning"
]
EOF

echo "✅ Created test package configuration"

# Clean and rebuild
echo "🧹 Cleaning previous build..."
rm -rf dist/ build/ *.egg-info/

echo "📦 Rebuilding package..."
python -m build

if [ $? -eq 0 ]; then
    echo "✅ Package rebuilt successfully!"
    echo ""
    echo "📋 New package contents:"
    ls -la dist/
    echo ""
    echo "🚀 Now try uploading again:"
    echo "   chmod +x debug_upload.sh"
    echo "   ./debug_upload.sh"
else
    echo "❌ Rebuild failed!"
    # Restore original
    mv pyproject.toml.backup pyproject.toml
    exit 1
fi
