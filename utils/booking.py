"""
予約リンク生成。

- 楽天トラベル：アプリID不要で使える検索URLに、日付・人数を埋め込む。
- じゃらん：ホテル料金APIの利用にはAPIキー登録が必要なため、
  まずは楽天トラベルAPIを優先する。じゃらんの検索結果は
  エリアID・宿泊日をURLパラメータで直接指定できず
  （旧`/ikisaki/{city}/` 形式は廃止済みで404になることを確認済み）、
  日付・人数を反映した検索URLを組み立てられないため、
  じゃらんnetのトップページへのリンクにとどめている。
  （将来：APIキー取得後 https://webservice.recruit.co.jp/doc/jalan/hotel/
    のじゃらんnet APIに切り替える）
- スカイスキャナー：航空券APIは審査が必要なため、
  検索結果ページのURLに日付・空港コードを埋め込んで代替する。

将来：各APIキーを取得したら、この差し替えだけで済むようにする。
"""

from utils.data import airport_codes

rakuten_city_codes = {
    '仙台': 'miyagi',
    '札幌': 'hokkaido',
    '東京': 'tokyo',
    '大阪': 'osaka',
    '名古屋': 'aichi',
    '福岡': 'fukuoka',
}


def get_jalan_hotel_url():
    """
    じゃらんnetのトップページのURLを返す。
    ホテル検索結果を日付・人数付きで直接指定するURL形式が
    確認できなかったため、トップページへのリンクにとどめている。
    """
    return "https://www.jalan.net/"


def get_rakuten_url(destination, checkin, checkout, num_people):
    """楽天トラベルのホテル検索結果ページのURLを返す（日付・人数を反映）"""
    city = rakuten_city_codes.get(destination, "")
    return (
        f"https://travel.rakuten.co.jp/yado/{city}/"
        f"?f_nen1={checkin.year}"
        f"&f_tuki1={checkin.month:02d}"
        f"&f_hi1={checkin.day:02d}"
        f"&f_nen2={checkout.year}"
        f"&f_tuki2={checkout.month:02d}"
        f"&f_hi2={checkout.day:02d}"
        f"&f_su={num_people}"
    )


def get_highway_bus_url():
    """
    高速バス検索サイトのURLを返す。
    じゃらんの高速バス予約サービスは2021年10月に終了しているため、
    現在稼働している高速バスネットの検索ページへのリンクに切り替えている。
    """
    return "https://www.kousokubus.net/BusRsv/ja/"


def get_skyscanner_url(departure, destination, date):
    """スカイスキャナーの航空券検索結果ページのURLを返す（日付を反映）"""
    dep = airport_codes.get(departure, "")
    arr = airport_codes.get(destination, "")
    date_str = date.strftime('%y%m%d')
    return (
        f"https://www.skyscanner.jp/transport/"
        f"flights/{dep}/{arr}/{date_str}/"
    )
