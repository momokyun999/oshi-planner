"""
じゃらんnet APIでホテルの実際の料金を取得する。
"""

import os

import requests
import streamlit as st
from xml.etree import ElementTree as ET

# Streamlit CloudではSecretsから、
# ローカルでは.envから読み込む
try:
    API_KEY = st.secrets.get("JALAN_API_KEY")
except Exception:
    API_KEY = None

if not API_KEY:
    from dotenv import load_dotenv
    load_dotenv()
    API_KEY = os.getenv("JALAN_API_KEY")

# 都市ごとのじゃらんエリアコード
AREA_CODES = {
    '仙台': '220000',
    '札幌': '010000',
    '東京': '130000',
    '大阪': '270000',
    '名古屋': '230000',
    '福岡': '400000',
}


@st.cache_data(ttl=300)
def get_hotel_prices(destination, checkin_str, checkout_str, num_people):
    """
    じゃらんAPIでホテルの最安値を取得する。

    返り値：
    {
        'min_price': 最安値（円）,
        'hotels': [
            {'name': ホテル名, 'price': 料金, 'url': 予約URL},
        ]
    }
    エラー時はNoneを返す
    """
    if not API_KEY:
        return None

    area_code = AREA_CODES.get(destination)
    if not area_code:
        return None

    try:
        # jws.jalan.netはHTTPSの応答がなくタイムアウトするため、
        # 実際に稼働しているHTTPエンドポイントを使用する
        url = "http://jws.jalan.net/APIAdvance/HotelSearch/V1/"
        params = {
            "key": API_KEY,
            "area_id": area_code,
            "checkin_date": checkin_str.replace("-", ""),
            "checkout_date": checkout_str.replace("-", ""),
            "adult_num": num_people,
            "hits": 5,
            "order": 1,  # 料金安い順
            "xml_cont": 1,
        }
        res = requests.get(url, params=params, timeout=10)
        root = ET.fromstring(res.content)

        hotels = []
        for hotel in root.findall(".//Hotel"):
            name = hotel.findtext("HotelName", "")
            price_text = hotel.findtext("MinCharge", "0")
            hotel_url = hotel.findtext("HotelURL", "")
            try:
                price = int(price_text)
            except ValueError:
                price = 0
            if name and price > 0:
                hotels.append({
                    "name": name,
                    "price": price,
                    "url": hotel_url,
                })

        if not hotels:
            return None

        return {
            "min_price": min(h["price"] for h in hotels),
            "hotels": hotels,
        }

    except Exception:
        return None
