
import datetime
import uuid

import plotly.graph_objects as go
import streamlit as st

from utils.calculator import calculate_split
from utils.storage import save_record
from utils.styles import alert, card, inject_theme, link_row, transport_card

# ============================================
# データ定義
# 将来：じゃらん・楽天トラベルAPIに切り替え予定
# ============================================

transport_data = {('東京', '仙台'): {'新幹線': {'料金': 11000, '時間': 90}, '高速バス': {'料金': 3500, '時間': 360}, '飛行機': {'料金': 15000, '時間': 75}}, ('東京', '札幌'): {'新幹線': {'料金': 22000, '時間': 240}, '高速バス': {'料金': 6000, '時間': 900}, '飛行機': {'料金': 12000, '時間': 90}}, ('東京', '大阪'): {'新幹線': {'料金': 14000, '時間': 150}, '高速バス': {'料金': 4000, '時間': 480}, '飛行機': {'料金': 13000, '時間': 75}}, ('東京', '名古屋'): {'新幹線': {'料金': 11000, '時間': 100}, '高速バス': {'料金': 3000, '時間': 360}, '飛行機': {'料金': 20000, '時間': 60}}, ('東京', '福岡'): {'新幹線': {'料金': 23000, '時間': 300}, '高速バス': {'料金': 8000, '時間': 1080}, '飛行機': {'料金': 14000, '時間': 105}}, ('仙台', '札幌'): {'新幹線': {'料金': 17000, '時間': 210}, '高速バス': {'料金': 5000, '時間': 480}, '飛行機': {'料金': 12000, '時間': 60}}, ('仙台', '大阪'): {'新幹線': {'料金': 22000, '時間': 240}, '高速バス': {'料金': 6000, '時間': 720}, '飛行機': {'料金': 14000, '時間': 80}}, ('仙台', '名古屋'): {'新幹線': {'料金': 17000, '時間': 180}, '高速バス': {'料金': 5000, '時間': 600}, '飛行機': {'料金': 15000, '時間': 75}}, ('仙台', '福岡'): {'新幹線': {'料金': 30000, '時間': 360}, '高速バス': {'料金': 9000, '時間': 1200}, '飛行機': {'料金': 15000, '時間': 90}}, ('札幌', '大阪'): {'新幹線': {'料金': 33000, '時間': 390}, '高速バス': {'料金': 10000, '時間': 1440}, '飛行機': {'料金': 15000, '時間': 105}}, ('札幌', '名古屋'): {'新幹線': {'料金': 28000, '時間': 330}, '高速バス': {'料金': 9000, '時間': 1200}, '飛行機': {'料金': 14000, '時間': 90}}, ('札幌', '福岡'): {'新幹線': {'料金': 40000, '時間': 480}, '高速バス': {'料金': 12000, '時間': 1800}, '飛行機': {'料金': 18000, '時間': 120}}, ('大阪', '名古屋'): {'新幹線': {'料金': 6500, '時間': 50}, '高速バス': {'料金': 2000, '時間': 180}, '飛行機': {'料金': 20000, '時間': 60}}, ('大阪', '福岡'): {'新幹線': {'料金': 15000, '時間': 150}, '高速バス': {'料金': 4000, '時間': 540}, '飛行機': {'料金': 12000, '時間': 75}}, ('名古屋', '福岡'): {'新幹線': {'料金': 18000, '時間': 210}, '高速バス': {'料金': 5000, '時間': 720}, '飛行機': {'料金': 14000, '時間': 90}}, ('仙台', '東京'): {'新幹線': {'料金': 11000, '時間': 90}, '高速バス': {'料金': 3500, '時間': 360}, '飛行機': {'料金': 15000, '時間': 75}}, ('札幌', '東京'): {'新幹線': {'料金': 22000, '時間': 240}, '高速バス': {'料金': 6000, '時間': 900}, '飛行機': {'料金': 12000, '時間': 90}}, ('大阪', '東京'): {'新幹線': {'料金': 14000, '時間': 150}, '高速バス': {'料金': 4000, '時間': 480}, '飛行機': {'料金': 13000, '時間': 75}}, ('名古屋', '東京'): {'新幹線': {'料金': 11000, '時間': 100}, '高速バス': {'料金': 3000, '時間': 360}, '飛行機': {'料金': 20000, '時間': 60}}, ('福岡', '東京'): {'新幹線': {'料金': 23000, '時間': 300}, '高速バス': {'料金': 8000, '時間': 1080}, '飛行機': {'料金': 14000, '時間': 105}}, ('札幌', '仙台'): {'新幹線': {'料金': 17000, '時間': 210}, '高速バス': {'料金': 5000, '時間': 480}, '飛行機': {'料金': 12000, '時間': 60}}, ('大阪', '仙台'): {'新幹線': {'料金': 22000, '時間': 240}, '高速バス': {'料金': 6000, '時間': 720}, '飛行機': {'料金': 14000, '時間': 80}}, ('名古屋', '仙台'): {'新幹線': {'料金': 17000, '時間': 180}, '高速バス': {'料金': 5000, '時間': 600}, '飛行機': {'料金': 15000, '時間': 75}}, ('福岡', '仙台'): {'新幹線': {'料金': 30000, '時間': 360}, '高速バス': {'料金': 9000, '時間': 1200}, '飛行機': {'料金': 15000, '時間': 90}}, ('大阪', '札幌'): {'新幹線': {'料金': 33000, '時間': 390}, '高速バス': {'料金': 10000, '時間': 1440}, '飛行機': {'料金': 15000, '時間': 105}}, ('名古屋', '札幌'): {'新幹線': {'料金': 28000, '時間': 330}, '高速バス': {'料金': 9000, '時間': 1200}, '飛行機': {'料金': 14000, '時間': 90}}, ('福岡', '札幌'): {'新幹線': {'料金': 40000, '時間': 480}, '高速バス': {'料金': 12000, '時間': 1800}, '飛行機': {'料金': 18000, '時間': 120}}, ('名古屋', '大阪'): {'新幹線': {'料金': 6500, '時間': 50}, '高速バス': {'料金': 2000, '時間': 180}, '飛行機': {'料金': 20000, '時間': 60}}, ('福岡', '大阪'): {'新幹線': {'料金': 15000, '時間': 150}, '高速バス': {'料金': 4000, '時間': 540}, '飛行機': {'料金': 12000, '時間': 75}}, ('福岡', '名古屋'): {'新幹線': {'料金': 18000, '時間': 210}, '高速バス': {'料金': 5000, '時間': 720}, '飛行機': {'料金': 14000, '時間': 90}}}

venues = {'仙台': ['宮城セキスイハイムスーパーアリーナ', '仙台PIT', 'ゼビオアリーナ仙台'], '札幌': ['北海道立総合体育センター（北海きたえーる）', '札幌ドーム', '札幌市民ホール'], '東京': ['東京ドーム', '日本武道館', 'さいたまスーパーアリーナ', '東京体育館', 'Zepp Shinjuku'], '大阪': ['大阪城ホール', '京セラドーム大阪', 'オリックス劇場', 'なんばHatch'], '名古屋': ['日本ガイシホール', 'ドルフィンズアリーナ', 'Zepp Nagoya'], '福岡': ['マリンメッセ福岡', 'PayPayドーム', 'Zepp Fukuoka']}

hotel_costs = {'仙台': {'ビジネス': 6000, 'ビジネス上': 9000, 'シティ': 13000}, '札幌': {'ビジネス': 7000, 'ビジネス上': 10000, 'シティ': 15000}, '東京': {'ビジネス': 9000, 'ビジネス上': 13000, 'シティ': 20000}, '大阪': {'ビジネス': 8000, 'ビジネス上': 11000, 'シティ': 17000}, '名古屋': {'ビジネス': 7000, 'ビジネス上': 10000, 'シティ': 15000}, '福岡': {'ビジネス': 7000, 'ビジネス上': 10000, 'シティ': 14000}}

cities = ["東京", "仙台", "札幌", "大阪", "名古屋", "福岡"]

# 予約リンク生成用の都市コード類
# 将来：各サービスの仕様変更に合わせて更新する
jalan_city_codes = {
    "仙台": "220000",
    "札幌": "010000",
    "東京": "130000",
    "大阪": "270000",
    "名古屋": "230000",
    "福岡": "400000",
}

bus_pref_codes = {
    "東京": "13",
    "仙台": "04",
    "札幌": "01",
    "大阪": "27",
    "名古屋": "23",
    "福岡": "40",
}

airport_codes = {
    "東京": "TYO",
    "仙台": "SDJ",
    "札幌": "CTS",
    "大阪": "OSA",
    "名古屋": "NGO",
    "福岡": "FUK",
}

# ============================================
# データ取得層（ここだけ差し替えれば拡張可能）
# ============================================

def get_transport_options(departure, destination):
    """
    交通手段と費用を返す。
    将来：各交通サービスのAPIに切り替える
    - 新幹線：JR東日本API
    - 高速バス：じゃらんバスAPI
    - 飛行機：各航空会社API
    """
    return transport_data.get((departure, destination), {})

def get_hotel_cost(city, hotel_type, nights):
    """
    宿泊費を返す。
    将来：じゃらんAPI・楽天トラベルAPIに切り替える
    """
    return hotel_costs[city][hotel_type] * nights

def is_busy_season(live_date):
    """
    繁忙期（年末年始・GW・お盆）かどうかを判定する。
    年末年始は年またぎ（12/28〜1/4）のため月日で判定する。
    """
    month, day = live_date.month, live_date.day
    if (month == 12 and day >= 28) or (month == 1 and day <= 4):
        return True
    if (month == 4 and day >= 28) or (month == 5 and day <= 6):
        return True
    if month == 8 and 10 <= day <= 18:
        return True
    return False

def get_booking_links(departure, destination, hotel_type, live_date):
    """
    予約リンクを（ホテル用, 交通手段用）のタプルで返す。
    リンク先は入力された日付を反映した検索結果ページ
    （概算・参考用）。
    将来：実際の予約URL・アフィリエイトリンクに切り替える
    """
    checkin = live_date
    checkout = live_date + datetime.timedelta(days=1)

    jalan_city = jalan_city_codes.get(destination, "")
    hotel_links = {
        "じゃらん": (
            f"https://www.jalan.net/ikisaki/{jalan_city}/"
            f"?stayFrom={checkin.strftime('%Y%m%d')}"
            f"&stayTo={checkout.strftime('%Y%m%d')}"
        ),
        "楽天トラベル": (
            "https://travel.rakuten.co.jp/yado/search/"
            f"?f_nen1={checkin.year}&f_tuki1={checkin.month:02d}"
            f"&f_hi1={checkin.day:02d}"
            f"&f_nen2={checkout.year}&f_tuki2={checkout.month:02d}"
            f"&f_hi2={checkout.day:02d}"
        ),
    }

    dpt_pref = bus_pref_codes.get(departure, "")
    arv_pref = bus_pref_codes.get(destination, "")
    dpt_airport = airport_codes.get(departure, "")
    arv_airport = airport_codes.get(destination, "")
    transport_links = {
        "新幹線（JR）": "https://www.jreast.co.jp/tabi/shinkansen/",
        "高速バス": (
            "https://highway-bus.jalan.net/"
            f"?dptPref={dpt_pref}&arvPref={arv_pref}"
            f"&month={checkin.strftime('%Y%m')}&day={checkin.strftime('%d')}"
        ),
        "飛行機": (
            "https://www.skyscanner.jp/transport/flights/"
            f"{dpt_airport}/{arv_airport}/{checkin.strftime('%y%m%d')}/"
        ),
    }
    return hotel_links, transport_links

# ============================================
# UI
# ============================================

st.set_page_config(
    page_title="推し活遠征プランナー",
    page_icon="🎤",
    layout="wide"
)

inject_theme()

st.title("🎤 推し活遠征プランナー")
st.caption("遠征にかかるすべての費用を、ここで計算。")

st.divider()

col1, col2 = st.columns(2)

with col1:
    with card():
        st.subheader("📍 遠征情報")
        departure = st.selectbox("出発地", cities)
        destination = st.selectbox(
            "ライブ会場（都市）",
            [c for c in cities if c != departure]
        )
        venue = st.selectbox("会場", venues[destination])
        live_date = st.date_input(
            "ライブ日程", value=datetime.date.today())
        if is_busy_season(live_date):
            alert(
                "繁忙期のため料金が高くなる可能性があります",
                kind="warning",
            )
        nights = st.number_input(
            "宿泊数", min_value=0, max_value=7, value=1)
        num_people = st.number_input(
            "人数", min_value=1, max_value=10, value=1)

with col2:
    with card():
        st.subheader("💴 予算設定")
        ticket_price = st.number_input(
            "チケット代（円）",
            min_value=0, value=8000, step=500)
        goods_budget = st.number_input(
            "グッズ予算（円）",
            min_value=0, value=10000, step=1000)
        food_budget = st.number_input(
            "食事・観光予算（円）",
            min_value=0, value=5000, step=1000)
        hotel_type = st.selectbox(
            "ホテルグレード",
            ["ビジネス", "ビジネス上", "シティ"]
        )

if st.button("費用を計算する", type="primary"):
    st.session_state.show_results = True

# 割り勘フォームの操作でも計算結果を表示し続けるため、
# ボタンの戻り値ではなくセッション状態で表示有無を管理する
if st.session_state.get("show_results"):
    st.divider()
    st.subheader("計算結果")

    route = get_transport_options(departure, destination)
    hotel_cost = get_hotel_cost(
        destination, hotel_type, nights)

    results = []
    for transport, data in route.items():
        transport_total = data["料金"] * 2 * num_people
        hotel_total = hotel_cost * num_people
        total = (
            transport_total
            + hotel_total
            + ticket_price * num_people
            + goods_budget
            + food_budget
        )
        results.append({
            "交通手段": transport,
            "交通費（往復）": transport_total,
            "所要時間": (
                f"{data['時間']//60}時間"
                f"{data['時間']%60}分"
            ),
            "宿泊費": hotel_total,
            "チケット代": ticket_price * num_people,
            "グッズ": goods_budget,
            "食事・観光": food_budget,
            "合計": total,
        })

    results.sort(key=lambda x: x["合計"])
    best = results[0]

    alert(
        f"最安：{best['交通手段']}を使うと合計 "
        f"<strong>{best['合計']:,}円</strong>（{num_people}人分）",
        kind="accent",
    )

    st.subheader("交通手段の比較")
    for r in results:
        is_best = r["交通手段"] == best["交通手段"]
        transport_card(
            r["交通手段"],
            r["交通費（往復）"],
            r["所要時間"],
            r["宿泊費"],
            r["合計"],
            is_best,
        )

    st.subheader("費用の内訳（最安プラン）")
    items = {
        "交通費（往復）": best["交通費（往復）"],
        "宿泊費": best["宿泊費"],
        "チケット代": best["チケット代"],
        "グッズ予算": best["グッズ"],
        "食事・観光": best["食事・観光"],
    }
    with card():
        fig = go.Figure(go.Bar(
            x=list(items.values()),
            y=list(items.keys()),
            orientation='h',
            marker_color='#6366F1',
        ))
        fig.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family='Inter',
            height=200,
            margin=dict(l=0, r=0, t=0, b=0),
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

    alert(
        f"{num_people}人で行く場合、1人あたり "
        f"<strong>{best['合計']//num_people:,}円</strong>かかります",
        kind="accent",
    )

    # ============================================
    # 予約リンク
    # 将来：実際の料金・空き状況を表示する
    # ============================================
    st.subheader("予約はこちらから")
    st.caption(
        "※ リンク先は入力した日付を反映した検索結果ページ"
        "（概算・参考用）です。"
    )
    hotel_links, transport_links = get_booking_links(
        departure, destination, hotel_type, live_date)

    st.markdown("**【ホテルを予約する】**")
    link_row(hotel_links)

    st.markdown("**【交通手段を予約する】**")
    link_row(transport_links)

    st.caption(
        "※ 交通費・宿泊費は概算です。"
        "実際の費用は時期や予約状況により異なります。"
    )

    # ============================================
    # 割り勘計算
    # ============================================
    st.divider()
    st.subheader("遠征メンバー・割り勘計算")

    members_input = st.text_input(
        "メンバー名を入力（カンマ区切り）",
        placeholder="例：ゆうたろう, さくら, はな",
        key="members_input",
    )
    members = [m.strip() for m in members_input.split(",") if m.strip()]

    if "payments" not in st.session_state:
        st.session_state.payments = []

    if not members:
        st.caption(
            "メンバー名を入力すると、支払い記録を"
            "登録できるようになります。"
        )
    else:
        with card():
            st.markdown("**各メンバーの支払い記録**")
            with st.form("payment_form", clear_on_submit=True):
                pcol1, pcol2, pcol3, pcol4 = st.columns([2, 2, 2, 1])
                payer = pcol1.selectbox("支払者", members)
                item = pcol2.text_input(
                    "項目名", placeholder="例：交通費")
                amount = pcol3.number_input(
                    "金額（円）", min_value=0, step=100)
                submitted = pcol4.form_submit_button("追加")
                if submitted and item and amount > 0:
                    st.session_state.payments.append({
                        "payer": payer,
                        "item": item,
                        "amount": amount,
                    })

            if st.session_state.payments:
                st.markdown("**登録済みの支払い**")
                for idx, p in enumerate(st.session_state.payments):
                    c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                    c1.write(p["payer"])
                    c2.write(p["item"])
                    c3.write(f"{p['amount']:,}円")
                    if c4.button("削除", key=f"del_payment_{idx}"):
                        st.session_state.payments.pop(idx)
                        st.rerun()

    split_result = None
    if members and st.session_state.payments:
        split_result = calculate_split(
            members, st.session_state.payments)

        with card():
            st.markdown("### 【割り勘計算結果】")
            st.write(
                "1人あたりの負担額: "
                f"**{split_result['per_person']:,.0f}円**"
            )

            st.markdown("**支払い一覧：**")
            for p in st.session_state.payments:
                st.write(
                    f"　{p['payer']}: {p['item']} {p['amount']:,}円"
                )

            st.markdown("**精算方法：**")
            if split_result["settlement"]:
                for s in split_result["settlement"]:
                    st.write(
                        f"{s['from']} → {s['to']} に "
                        f"{s['amount']:,}円"
                    )
            else:
                st.write(
                    "精算の必要はありません"
                    "（全員の負担額が同じです）"
                )

    # ============================================
    # 遠征記録の保存
    # ============================================
    st.divider()
    st.subheader("この遠征を記録する")
    memo = st.text_area(
        "メモ（自由記入）",
        placeholder="例：アリーナAブロックで神席だった！",
        key="record_memo",
    )

    if st.button("記録する"):
        record = {
            "id": str(uuid.uuid4()),
            "created_at": datetime.datetime.now().isoformat(
                timespec="seconds"),
            "live_date": live_date.isoformat(),
            "departure": departure,
            "destination": destination,
            "venue": venue,
            "transport": best["交通手段"],
            "transport_cost": best["交通費（往復）"],
            "hotel_cost": best["宿泊費"],
            "nights": nights,
            "num_people": num_people,
            "ticket_price": ticket_price,
            "goods_budget": goods_budget,
            "food_budget": food_budget,
            "hotel_type": hotel_type,
            "total_cost": best["合計"],
            "members": members,
            "payments": st.session_state.payments,
            "settlement": (
                split_result["settlement"] if split_result else []
            ),
            "memo": memo,
        }
        save_record(record)
        alert(
            "記録を保存しました！"
            "サイドバーの「mypage」ページから確認できます。",
            kind="success",
        )
