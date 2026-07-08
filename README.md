# 推し活遠征プランナー

## 環境変数（楽天トラベルAPI）

ホテルの実勢価格取得に楽天トラベルAPIを使用します。以下のキーが必要です。

- `RAKUTEN_APP_ID`
- `RAKUTEN_AFFILIATE_ID`
- `RAKUTEN_ACCESS_KEY`

ローカル開発では、プロジェクト直下に `.env` ファイルを作成して設定します（`.env` は `.gitignore` 済みでリポジトリにはコミットされません）。

```
RAKUTEN_APP_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
RAKUTEN_AFFILIATE_ID=xxxxxxxx.xxxxxxxx.xxxxxxxx.xxxxxxxx
RAKUTEN_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**注意：** 実際のキー値は `.env` ファイルにのみ記載し、READMEやコード、Gitにコミットするファイルには書かないでください。

### Streamlit Cloudへのデプロイ時（Secretsの設定）

Streamlit Cloud上では `.env` は読み込まれないため、管理画面からSecretsとして設定します。

1. https://share.streamlit.io を開く
2. oshi-plannerアプリの「⋮」→「Settings」を開く
3. 「Secrets」タブを開く
4. 以下の形式でキーと値を入力して保存する（値は自分の実際のキーに置き換える）：

```toml
RAKUTEN_APP_ID = "自分のRAKUTEN_APP_ID"
RAKUTEN_AFFILIATE_ID = "自分のRAKUTEN_AFFILIATE_ID"
RAKUTEN_ACCESS_KEY = "自分のRAKUTEN_ACCESS_KEY"
```

Secretsに保存した値はStreamlit Cloud側でのみ保持され、リポジトリには含まれません。
