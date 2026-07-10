# 推し活遠征プランナー 現地情報機能追加 指示書
## 天気予報・雨雲レーダー・時刻表リンク

---

## 目的

「費用計算ツール」から「遠征のお供アプリ」へ進化させる第一歩として、
遠征先の天気予報・雨雲レーダー・現地交通の時刻表リンクを追加する。

---

## 機能1：天気予報（OpenWeatherMap API）

### APIキーの取得（ユーザー側で実施済みの想定）

OpenWeatherMap（無料プラン）を使用する。
.envファイルに以下が追加される想定：

```
OPENWEATHER_API_KEY=（実際のAPIキー）
```

※ユーザーがまだ取得していない場合は、
  https://openweathermap.org/api で
  無料アカウントを作成しAPIキーを取得する必要がある旨を
  READMEに記載すること。

### utils/weather_api.py を新規作成

```python
import os
import requests
import streamlit as st
from datetime import datetime

try:
    API_KEY = st.secrets.get("OPENWEATHER_API_KEY")
except Exception:
    API_KEY = None

if not API_KEY:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

# 都市ごとの緯度・経度
CITY_COORDS = {
    '仙台': (38.2682, 140.8694),
    '札幌': (43.0621, 141.3544),
    '東京': (35.6762, 139.6503),
    '大阪': (34.6937, 135.5023),
    '名古屋': (35.1815, 136.9066),
    '福岡': (33.5904, 130.4017),
}

# 天気の日本語変換
WEATHER_JA = {
    "Clear": "☀️ 晴れ",
    "Clouds": "☁️ くもり",
    "Rain": "🌧️ 雨",
    "Drizzle": "🌦️ 小雨",
    "Thunderstorm": "⛈️ 雷雨",
    "Snow": "❄️ 雪",
    "Mist": "🌫️ 霧",
    "Fog": "🌫️ 霧",
    "Haze": "🌫️ かすみ",
}

@st.cache_data(ttl=1800)  # 30分キャッシュ
def get_weather_forecast(city, target_date_str):
    """
    指定都市・日付の天気予報を取得する。
    OpenWeatherMapの5日間予報（3時間ごと）を使い、
    target_dateに最も近い予報を返す。

    返り値：
    {
        'weather': '☀️ 晴れ',
        'temp': 気温（℃）,
        'temp_min': 最低気温,
        'temp_max': 最高気温,
        'humidity': 湿度（%）,
        'pop': 降水確率（%）,
        'wind': 風速（m/s）,
        'available': True/False,  # 予報範囲内か
    }
    エラー時はNoneを返す
    """
    if not API_KEY:
        return None

    coords = CITY_COORDS.get(city)
    if not coords:
        return None

    lat, lon = coords

    try:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": API_KEY,
            "units": "metric",
            "lang": "ja",
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        if data.get("cod") != "200":
            return None

        # target_dateに最も近い予報を探す
        target = datetime.strptime(target_date_str, "%Y-%m-%d").date()

        # 昼12時前後の予報を優先的に取得
        best = None
        best_diff = None
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            if dt.date() == target:
                # 12時に近いものを選ぶ
                diff = abs(dt.hour - 12)
                if best_diff is None or diff < best_diff:
                    best = item
                    best_diff = diff

        if best is None:
            # 予報範囲外（5日以上先）
            return {"available": False}

        weather_main = best["weather"][0]["main"]
        return {
            "weather": WEATHER_JA.get(
                weather_main, best["weather"][0]["description"]
            ),
            "temp": round(best["main"]["temp"]),
            "temp_min": round(best["main"]["temp_min"]),
            "temp_max": round(best["main"]["temp_max"]),
            "humidity": best["main"]["humidity"],
            "pop": round(best.get("pop", 0) * 100),
            "wind": round(best["wind"]["speed"], 1),
            "available": True,
        }

    except Exception:
        return None
```

### 表示への組み込み（oshi_planner.py）

計算結果セクションに「現地の天気」カードを追加する：

```python
from utils.weather_api import get_weather_forecast

weather = get_weather_forecast(
    destination, live_date.strftime("%Y-%m-%d")
)

st.subheader("🌤️ 現地の天気")

if weather is None:
    st.caption("天気情報を取得できませんでした。")
elif not weather.get("available"):
    st.info(
        "この日程はまだ天気予報の範囲外です"
        "（5日先まで対応）。遠征が近づいたら"
        "再度ご確認ください。"
    )
else:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("天気", weather["weather"])
    col2.metric(
        "気温",
        f"{weather['temp']}℃",
        f"最高{weather['temp_max']}/最低{weather['temp_min']}"
    )
    col3.metric("降水確率", f"{weather['pop']}%")
    col4.metric("湿度", f"{weather['humidity']}%")

    # 服装・持ち物アドバイス
    advice = []
    if weather["pop"] >= 50:
        advice.append("傘を持っていきましょう")
    if weather["temp_max"] >= 30:
        advice.append("暑さ対策（水分・日傘）を")
    if weather["temp_min"] <= 5:
        advice.append("防寒対策をしっかりと")
    if weather["wind"] >= 8:
        advice.append("風が強いので注意")
    if advice:
        st.caption("💡 " + " / ".join(advice))
```

---

## 機能2：雨雲レーダー

OpenWeatherMapの雨雲レーダーは実装が複雑なため、
Yahoo!天気の雨雲レーダーページへのリンク誘導とする。

```python
# 都市ごとのYahoo天気 地域コード
YAHOO_WEATHER_CODES = {
    '仙台': '0400',  # 宮城県
    '札幌': '0100',  # 北海道
    '東京': '1300',  # 東京都
    '大阪': '2700',  # 大阪府
    '名古屋': '2300', # 愛知県
    '福岡': '4000',  # 福岡県
}

def get_rain_radar_url(city):
    code = YAHOO_WEATHER_CODES.get(city, '')
    return f"https://weather.yahoo.co.jp/weather/jp/{code}/"
```

天気カードの下に雨雲レーダーへのリンクを表示：

```python
radar_url = get_rain_radar_url(destination)
st.markdown(
    f'<a href="{radar_url}" target="_blank" '
    f'rel="noopener noreferrer" '
    f'style="display:inline-block; padding:8px 16px; '
    f'background:#F3F4F6; color:#1A1A1A; '
    f'border-radius:6px; text-decoration:none; '
    f'font-size:14px; border:1px solid #E5E7EB;">'
    f'🌧️ {destination}の雨雲レーダーを見る →</a>',
    unsafe_allow_html=True
)
```

---

## 機能3：現地交通の時刻表（リンク誘導）

無料で確実な方法として、Yahoo!乗換案内への
リンク誘導を実装する。

### 会場最寄り駅データを追加

```python
# 会場ごとの最寄り駅
VENUE_STATIONS = {
    '宮城セキスイハイムスーパーアリーナ': '利府駅',
    '仙台PIT': '仙台駅',
    'ゼビオアリーナ仙台': '長町駅',
    '北海道立総合体育センター（北海きたえーる）': '豊平公園駅',
    '札幌ドーム': '福住駅',
    '札幌市民ホール': '大通駅',
    '東京ドーム': '水道橋駅',
    '日本武道館': '九段下駅',
    'さいたまスーパーアリーナ': 'さいたま新都心駅',
    '東京体育館': '千駄ヶ谷駅',
    'Zepp Shinjuku': '新宿駅',
    '大阪城ホール': '大阪城公園駅',
    '京セラドーム大阪': 'ドーム前駅',
    'オリックス劇場': '本町駅',
    'なんばHatch': 'なんば駅',
    '日本ガイシホール': '笠寺駅',
    'ドルフィンズアリーナ': '名古屋駅',
    'Zepp Nagoya': '名古屋駅',
    'マリンメッセ福岡': '博多駅',
    'PayPayドーム': '唐人町駅',
    'Zepp Fukuoka': '西鉄平尾駅',
}

def get_transit_url(from_station, to_station):
    """Yahoo!乗換案内の検索URLを生成"""
    return (
        f"https://transit.yahoo.co.jp/search/result"
        f"?from={from_station}&to={to_station}"
    )
```

### 表示への組み込み

「現地の交通」セクションを追加する：

```python
st.subheader("🚃 現地の交通")

nearest_station = VENUE_STATIONS.get(venue, "")

if nearest_station:
    st.write(f"**{venue}** の最寄り駅：{nearest_station}")

    # 主要駅から会場までの経路検索リンク
    # 目的地都市の代表駅を出発地の例として設定
    major_stations = {
        '仙台': '仙台駅',
        '札幌': '札幌駅',
        '東京': '東京駅',
        '大阪': '大阪駅',
        '名古屋': '名古屋駅',
        '福岡': '博多駅',
    }
    hub_station = major_stations.get(destination, "")

    if hub_station and hub_station != nearest_station:
        transit_url = get_transit_url(hub_station, nearest_station)
        st.markdown(
            f'<a href="{transit_url}" target="_blank" '
            f'rel="noopener noreferrer" '
            f'style="display:inline-block; padding:8px 16px; '
            f'background:#F3F4F6; color:#1A1A1A; '
            f'border-radius:6px; text-decoration:none; '
            f'font-size:14px; border:1px solid #E5E7EB; '
            f'margin:4px 0;">'
            f'🚃 {hub_station}→{nearest_station} の経路を調べる →</a>',
            unsafe_allow_html=True
        )

    st.caption(
        "※出発駅は乗換案内のページで自由に変更できます"
    )
else:
    st.caption("この会場の最寄り駅情報は準備中です。")
```

---

## READMEへの追記

OpenWeatherMap APIキーの取得手順と
Streamlit Secrets設定手順を追記する：

```
## 天気予報機能の設定

1. https://openweathermap.org/api で
   無料アカウントを作成
2. API Keysページでキーを取得
3. ローカル: .envに OPENWEATHER_API_KEY=xxx を追加
4. Streamlit Cloud: Settings→Secretsに
   OPENWEATHER_API_KEY = "xxx" を追加
```

---

## 実装の優先順位

```
STEP1: 天気予報（機能1）
STEP2: 雨雲レーダーリンク（機能2）
STEP3: 時刻表リンク（機能3）
```

---

## 注意事項

- .env・APIキーは絶対にGitHubにpushしない
- OpenWeatherMap無料プランは5日先までの予報
  → それ以降は「予報範囲外」と表示する
- 天気APIが失敗しても他の機能に影響しないよう
  必ずtry-exceptでフォールバックする
- 既存の計算・割り勘・記録機能は変更しない
- リンクはすべて st.markdown のaタグ（target="_blank"）で実装
  （st.link_buttonはStreamlit Cloudで不具合があったため）

---

## 実装後の確認事項

ブラウザで以下を確認してから報告：
1. 5日以内の日程で天気予報が表示されるか
2. 5日より先の日程で「予報範囲外」と表示されるか
3. 服装アドバイスが条件に応じて表示されるか
4. 雨雲レーダーのリンクが外部サイトに飛べるか
5. 時刻表（乗換案内）のリンクが飛べるか
6. APIキー未設定でもアプリが落ちないか

---

## GitHub push

確認完了後、以下を実行してpushする（.envは含めない）：

```bash
git add .
git commit -m "現地情報機能追加：天気予報・雨雲レーダー・時刻表リンク"
git push
```

pushが完了したら「完了」と報告する。
```
