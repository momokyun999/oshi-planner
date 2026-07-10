"""
現地情報（雨雲レーダー・乗換案内）のリンク生成。

- 雨雲レーダー：OpenWeatherMapの雨雲レーダーは実装が複雑なため、
  Yahoo!天気の雨雲レーダーページへのリンク誘導とする。
- 時刻表：無料で確実な方法として、Yahoo!乗換案内へのリンク誘導とする。
"""

from utils.data import yahoo_weather_codes


def get_rain_radar_url(city):
    """Yahoo!天気の雨雲レーダーページのURLを返す"""
    code = yahoo_weather_codes.get(city, "")
    return f"https://weather.yahoo.co.jp/weather/jp/{code}/"


def get_transit_url(from_station, to_station):
    """Yahoo!乗換案内の検索URLを生成"""
    return (
        f"https://transit.yahoo.co.jp/search/result"
        f"?from={from_station}&to={to_station}"
    )
