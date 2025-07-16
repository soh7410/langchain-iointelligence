#!/bin/bash

echo "🐙 GitHub Repository Setup for langchain-iointelligence"
echo "====================================================="

# 1. Git初期化
echo "📁 Initializing Git repository..."
git init

# 2. .gitignoreファイルの作成
echo "📝 Creating .gitignore..."
cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.
#   However, in case of collaboration, if having platform-specific dependencies or dependencies
#   having no cross-platform support, pipenv may install dependencies that don't work, or not
#   install all needed dependencies.
#Pipfile.lock

# PEP 582; used by e.g. github.com/David-OConnor/pyflow
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Backup files
*.bak
*.backup

# PyPI credentials
.pypirc

# Build scripts output
test_*_env/
EOF

# 3. 全ファイルをステージング
echo "📦 Adding files to Git..."
git add .

# 4. 初回コミット
echo "💾 Creating initial commit..."
git commit -m "Initial commit: langchain-iointelligence v$(python setup.py --version)

- LangChain wrapper for io Intelligence LLM API
- OpenAI-compatible API format support
- Environment variable configuration
- Comprehensive test suite
- English documentation for international use
- Published on PyPI"

# 5. メインブランチに変更
git branch -M main

echo "✅ Git repository initialized successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Create a new repository on GitHub:"
echo "   https://github.com/new"
echo "2. Repository name: langchain-iointelligence"
echo "3. Description: LangChain wrapper for io Intelligence LLM API"
echo "4. Make it public"
echo "5. Do NOT initialize with README, .gitignore, or license (we have them)"
echo ""
echo "6. Then run these commands:"
echo "   git remote add origin https://github.com/YOUR_USERNAME/langchain-iointelligence.git"
echo "   git push -u origin main"
echo ""
echo "📋 Repository will include:"
echo "- ✅ Source code"
echo "- ✅ Documentation"
echo "- ✅ Tests"
echo "- ✅ Examples"
echo "- ✅ License"
echo "- ✅ .gitignore"
