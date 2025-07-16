#!/bin/bash

echo "📁 Current Project Structure Analysis"
echo "===================================="

echo "✅ Files that WILL be uploaded to GitHub:"
echo "----------------------------------------"
find . -type f \
  ! -path "./dist/*" \
  ! -path "./build/*" \
  ! -path "./*.egg-info/*" \
  ! -path "./__pycache__/*" \
  ! -path "./.*" \
  ! -name "*.pyc" \
  ! -name "*.pyo" \
  ! -name "*.bak" \
  ! -name "*.backup" \
  ! -name ".pypirc" \
  | sort

echo ""
echo "❌ Files that will be IGNORED by Git:"
echo "------------------------------------"
find . -type f \( \
  -path "./dist/*" -o \
  -path "./build/*" -o \
  -path "./*.egg-info/*" -o \
  -path "./__pycache__/*" -o \
  -name "*.pyc" -o \
  -name "*.pyo" -o \
  -name "*.bak" -o \
  -name "*.backup" \
\) | sort

echo ""
echo "📦 PyPI Distribution Files (ignored):"
echo "------------------------------------"
ls -la dist/ 2>/dev/null || echo "No dist/ directory found"

echo ""
echo "🏗️ Build Files (ignored):"
echo "-------------------------"
ls -la build/ 2>/dev/null || echo "No build/ directory found"

echo ""
echo "📋 Summary:"
echo "----------"
echo "✅ Source code and documentation → GitHub"
echo "❌ Build artifacts and credentials → .gitignore"
echo "📦 PyPI gets built from source when needed"
