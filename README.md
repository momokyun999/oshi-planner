# 推し活遠征プランナー

## 環境変数（じゃらんnet API）

ホテルの実勢価格取得にじゃらんnet APIを使用します。以下のキーが必要です。

- `JALAN_API_KEY`

ローカル開発では、プロジェクト直下に `.env` ファイルを作成して設定します（`.env` は `.gitignore` 済みでリポジトリにはコミットされません）。

```
JALAN_API_KEY=xxxxxxxxxxxxxxxx
```

**注意：** 実際のキー値は `.env` ファイルにのみ記載し、READMEやコード、Gitにコミットするファイルには書かないでください。

## 天気予報機能の設定

現地の天気予報にOpenWeatherMap APIを使用します。以下のキーが必要です。

- `OPENWEATHER_API_KEY`

1. https://openweathermap.org/api で無料アカウントを作成
2. API Keysページでキーを取得
3. ローカル: `.env` に以下を追加

```
OPENWEATHER_API_KEY=xxxxxxxxxxxxxxxx
```

APIキーが未設定の場合、天気予報カードは表示されず「天気情報を取得できませんでした。」と表示されるだけで、他の機能には影響しません。

### Streamlit Cloudへのデプロイ時（Secretsの設定）

Streamlit Cloud上では `.env` は読み込まれないため、管理画面からSecretsとして設定します。

1. https://share.streamlit.io を開く
2. oshi-plannerアプリの「⋮」→「Settings」を開く
3. 「Secrets」タブを開く
4. 以下の形式でキーと値を入力して保存する（値は自分の実際のキーに置き換える）：

```toml
JALAN_API_KEY = "自分のJALAN_API_KEY"
OPENWEATHER_API_KEY = "自分のOPENWEATHER_API_KEY"
```

Secretsに保存した値はStreamlit Cloud側でのみ保持され、リポジトリには含まれません。
