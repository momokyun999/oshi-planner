"""
楽天トラベルAPIでホテルの実際の料金を取得する。
"""

import os

import requests
import streamlit as st

# Streamlit CloudではSecretsから、
# ローカルでは.envから読み込む
try:
    APP_ID = st.secrets.get("RAKUTEN_APP_ID")
except Exception:
    APP_ID = None

if not APP_ID:
    from dotenv import load_dotenv
    load_dotenv()
    APP_ID = os.getenv("RAKUTEN_APP_ID")

# 都市ごとの楽天トラベルエリアコード
AREA_CODES = {
    '仙台': '04',
    '札幌': '01',
    '東京': '13',
    '大阪': '27',
    '名古屋': '23',
    '福岡': '40',
}


@st.cache_data(ttl=300)  # 5分間キャッシュ
def get_hotel_prices(destination, checkin_str, checkout_str, num_people):
    """
    楽天トラベルAPIでホテルの最安値を取得する。
    キャッシュのためdateオブジェクトではなく文字列で受け取る。

    返り値：
    {
        'min_price': 最安値（円）,
        'hotels': [
            {'name': ホテル名, 'price': 料金, 'url': 予約URL},
        ]
    }
    エラー時はNoneを返す
    """
    if not APP_ID:
        return None

    pref_code = AREA_CODES.get(destination)
    if not pref_code:
        return None

    try:
        url = (
            "https://app.rakuten.co.jp/services/api/"
            "Travel/SimpleHotelSearch/20170426"
        )
        params = {
            "applicationId": APP_ID,
            "formatVersion": 2,
            "checkinDate": checkin_str,
            "checkoutDate": checkout_str,
            "adultNum": num_people,
            "middleAreaCode": pref_code,
            "hits": 5,
            "sort": "+roomCharge",
        }
        res = requests.get(url, params=params, timeout=10)
        data = res.json()

        hotels = []
        for hotel in data.get("hotels", []):
            info = hotel[0]["hotelBasicInfo"]
            hotels.append({
                "name": info["hotelName"],
                "price": info.get("hotelMinCharge", 0),
                "url": info["hotelInformationUrl"],
            })

        if not hotels:
            return None

        return {
            "min_price": min(h["price"] for h in hotels),
            "hotels": hotels,
        }

    except Exception:
        return None
