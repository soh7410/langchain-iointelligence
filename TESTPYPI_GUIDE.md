# 📦 Test PyPI アップロード手順

## 🚀 事前準備

### 1. Test PyPI アカウント作成
1. https://test.pypi.org/ でアカウント作成
2. メール認証を完了

### 2. API トークン作成
1. https://test.pypi.org/manage/account/token/ にアクセス
2. "Add API token" をクリック
3. Token name: `langchain-iointelligence-upload`
4. Scope: "Entire account" を選択
5. トークンをコピー（`pypi-` で始まる）

## 📋 アップロード実行

```bash
cd /Users/soheiyagi/sou-co/langchain-iointelligence

# Test PyPI にアップロード
chmod +x upload_test_pypi.sh
./upload_test_pypi.sh
```

**プロンプトが表示されたら:**
- Username: `__token__`
- Password: コピーしたAPIトークン（`pypi-AgEIcHl...` の形式）

## 🧪 インストールテスト

### 新しい環境でテスト
```bash
# 新しい仮想環境を作成
python -m venv test_env
source test_env/bin/activate  # macOS/Linux
# または test_env\Scripts\activate  # Windows

# Test PyPI からインストール
pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence

# 依存関係を通常のPyPIから追加インストール
pip install langchain-core requests python-dotenv

# テスト実行
python test_pypi_install.py
```

## ✅ 期待される結果

### アップロード成功時
```
🎉 Successfully uploaded to Test PyPI!

📦 Test installation:
   pip install --index-url https://test.pypi.org/simple/ langchain-iointelligence

🔗 View on Test PyPI:
   https://test.pypi.org/project/langchain-iointelligence/
```

### インストールテスト成功時
```
🎉 All Test PyPI installation tests passed!

📝 Package is working correctly from Test PyPI
✅ Ready for production PyPI upload
```

## 🚨 トラブルシューティング

### よくある問題

1. **"Package already exists" エラー**
   - 解決: `pyproject.toml` のバージョンを上げる（例: 0.2.0 → 0.2.1）

2. **"Invalid credentials" エラー**
   - 解決: APIトークンが正しいか確認
   - Username は必ず `__token__` を使用

3. **"Dependencies not found" エラー**
   - 解決: Test PyPI には依存関係がない場合がある
   - 通常のPyPIから依存関係を手動インストール

4. **Import エラー**
   - 解決: パッケージ名を確認（`langchain_iointelligence` vs `langchain-iointelligence`）

## 🎯 次のステップ

Test PyPIで正常動作を確認後:

1. **本番PyPIアカウント作成**: https://pypi.org/
2. **本番PyPI APIトークン作成**: https://pypi.org/manage/account/token/
3. **本番PyPIにアップロード**: `python -m twine upload dist/*`

## 📚 参考リンク

- [Test PyPI](https://test.pypi.org/)
- [Twine Documentation](https://twine.readthedocs.io/)
- [Python Packaging Guide](https://packaging.python.org/)
