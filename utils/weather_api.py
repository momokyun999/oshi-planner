"""
OpenWeatherMap APIで遠征先の天気予報を取得する。
"""

import os
from datetime import datetime

import requests
import streamlit as st

# Streamlit CloudではSecretsから、
# ローカルでは.envから読み込む
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
