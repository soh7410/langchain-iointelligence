# PyPI公開完全ガイド

## 📋 事前準備チェックリスト

### ✅ 必要なアカウント
- [ ] PyPIアカウント (https://pypi.org/account/register/)
- [ ] TestPyPIアカウント (https://test.pypi.org/account/register/)

### ✅ 必要なツール
```bash
pip install build twine
```

### ✅ 必要なファイル
- [ ] setup.py
- [ ] pyproject.toml
- [ ] README.md
- [ ] LICENSE
- [ ] langchain_iointelligence/__init__.py
- [ ] langchain_iointelligence/llm.py

## 🚀 公開手順

### ステップ1: 事前チェック
```bash
chmod +x pre_publish_check.sh
./pre_publish_check.sh
```

### ステップ2: TestPyPIでテスト公開
```bash
chmod +x publish_to_pypi.sh
./publish_to_pypi.sh test
```

### ステップ3: テスト環境での確認
```bash
# 新しい仮想環境を作成
python -m venv test_env
source test_env/bin/activate

# TestPyPIからインストール
pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence

# 動作確認
python -c "
from langchain_iointelligence import IOIntelligenceLLM
print('✅ Import successful')
llm = IOIntelligenceLLM(api_key='test', api_url='https://test.com')
print('✅ Initialization successful')
"

deactivate
rm -rf test_env
```

### ステップ4: 本番PyPIに公開
```bash
./publish_to_pypi.sh prod
```

### ステップ5: 公開後の確認
```bash
chmod +x post_publish_check.sh
./post_publish_check.sh
```

## 🔧 手動での公開手順

### TestPyPI公開
```bash
# ビルド
python -m build

# TestPyPIにアップロード
python -m twine upload --repository testpypi dist/*

# TestPyPIからインストール
pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence
```

### 本番PyPI公開
```bash
# クリーンビルド
rm -rf dist/ build/ *.egg-info/
python -m build

# 検証
python -m twine check dist/*

# PyPIにアップロード
python -m twine upload dist/*
```

## 📊 公開後の管理

### バージョン更新
```bash
# setup.pyとpyproject.tomlのバージョンを更新
# 例: 0.2.0 → 0.2.1

# 再ビルド・再公開
python -m build
python -m twine upload dist/*
```

### 統計確認
- PyPI: https://pypi.org/project/langchain-iointelligence/
- 統計: https://pypistats.org/packages/langchain-iointelligence
- ダウンロード: https://pepy.tech/project/langchain-iointelligence

## 🎯 成功の確認

### ✅ 成功指標
- [ ] PyPIページで確認可能
- [ ] `pip install langchain-iointelligence`でインストール可能
- [ ] バッジがREADMEに表示される
- [ ] 正常にインポート・使用可能

### 📝 公開後のタスク
1. GitHubリポジトリの作成・更新
2. ドキュメントサイトの作成
3. コミュニティでの共有
4. ユーザーフィードバックの収集
5. 継続的な改善とメンテナンス

## ⚠️ 注意事項

### 🔐 セキュリティ
- APIキーは絶対に公開しない
- .envファイルを.gitignoreに追加
- 個人情報を含めない

### 📝 ライセンス
- MIT Licenseを使用
- 著作権表示を忘れずに

### 🔄 バージョン管理
- Semantic Versioningを使用
- 破壊的変更は Major version で
- 機能追加は Minor version で
- バグ修正は Patch version で

## 🆘 トラブルシューティング

### よくある問題
1. **アップロードエラー**: パッケージ名の重複
2. **ビルドエラー**: setup.pyの設定問題
3. **インストールエラー**: 依存関係の問題

### 解決方法
```bash
# パッケージ名の確認
pip search langchain-iointelligence

# 依存関係の確認
pip install --dry-run langchain-iointelligence

# ビルドの詳細確認
python -m build --verbose
```
