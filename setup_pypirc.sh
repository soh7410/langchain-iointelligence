#!/bin/bash

echo "🔧 .pypirc ファイルを作成"
echo "======================"

echo "TestPyPIのAPIトークンを入力してください（pypi- で始まる）:"
read -s TESTPYPI_TOKEN

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

echo "✅ .pypirc ファイルを作成しました"
echo "🚀 再度アップロードを試します..."

python -m twine upload --repository testpypi dist/*

echo "🔍 認証情報を確認したい場合:"
echo "cat ~/.pypirc"
