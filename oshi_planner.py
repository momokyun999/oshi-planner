
import datetime
import uuid

import plotly.graph_objects as go
import streamlit as st

from utils.booking import (
    get_highway_bus_url,
    get_jalan_hotel_url,
    get_rakuten_url,
    get_skyscanner_url,
)
from utils.calculator import calculate_split
from utils.data import cities, hotel_costs, transport_data, venues
from utils.jalan_api import get_hotel_prices
from utils.sidebar import render_sidebar
from utils.storage import save_record
from utils.styles import alert, card, inject_theme, link_row, transport_card

DEFAULT_HOTEL_GRADE = "ビジネス"

# ============================================
# データ取得層（ここだけ差し替えれば拡張可能）
# ============================================

def get_transport_options(departure, destination):
    """
    交通手段と費用を返す。
    将来：各交通サービスのAPIに切り替える
    - 新幹線：JR東日本API
    - 高速バス：高速バスネットAPI
    - 飛行機：各航空会社API
    """
    return transport_data.get((departure, destination), {})

def get_hotel_cost(city, nights):
    """
    宿泊費を返す。目安料金として各都市の最も安いグレード
    （hotel_costs[city]["ビジネス"]）を使って計算する。
    将来：じゃらんAPI・楽天トラベルAPIに切り替える
    """
    return hotel_costs[city][DEFAULT_HOTEL_GRADE] * nights

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

def get_booking_links(departure, destination, live_date, num_people):
    """
    予約リンクを（ホテル用, 交通手段用）のタプルで返す。
    リンク先は入力された日付・人数を反映した検索結果ページ
    （概算・参考用）。
    将来：実際の予約URL・アフィリエイトリンクに切り替える
    """
    checkin = live_date
    checkout = live_date + datetime.timedelta(days=1)

    hotel_links = {
        "じゃらん": get_jalan_hotel_url(),
        "楽天トラベル（日付・人数反映）": get_rakuten_url(
            destination, checkin, checkout, num_people),
    }

    transport_links = {
        "新幹線（JR）": "https://www.jreast.co.jp/tabi/shinkansen/",
        "高速バス（高速バスネット）": get_highway_bus_url(),
        "飛行機（スカイスキャナー・日付反映）": get_skyscanner_url(
            departure, destination, checkin),
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
render_sidebar()


def fmt_amount(amount):
    """表示設定の通貨表示ON/OFFに応じて金額を整形する"""
    if st.session_state.get("show_currency", True):
        return f"{amount:,}円"
    return f"{amount:,}"


st.title("🎤 推し活遠征プランナー")
st.caption("遠征にかかるすべての費用を、ここで計算。")

st.divider()

col1, col2 = st.columns(2)

with col1:
    with card():
        st.subheader("📍 遠征情報")
        departure = st.selectbox(
            "出発地", cities, help="出発する都市を選んでください")
        destination = st.selectbox(
            "ライブ会場（都市）",
            [c for c in cities if c != departure],
            help="ライブ・イベントが開催される都市を選んでください",
        )
        venue = st.selectbox(
            "会場", venues[destination],
            help="具体的な会場名を選んでください")
        live_date = st.date_input(
            "ライブ日程", value=datetime.date.today(),
            help="ライブ・イベント当日の日付を入力してください")
        if is_busy_season(live_date) and st.session_state.get(
                "show_busy_warning", True):
            alert(
                "繁忙期のため料金が高くなる可能性があります",
                kind="warning",
            )
        nights = st.number_input(
            "宿泊数", min_value=0, max_value=7, value=1,
            help="現地に宿泊する日数を入力してください")
        num_people = st.number_input(
            "人数", min_value=1, max_value=10, value=1,
            help="一緒に遠征する人数（自分を含む）を入力してください")

with col2:
    with card():
        st.subheader("💴 予算設定")
        ticket_price = st.number_input(
            "チケット代（円）",
            min_value=0, value=8000, step=500,
            help="1人分のチケット代を入力してください")
        goods_budget = st.number_input(
            "グッズ予算（円）",
            min_value=0, value=10000, step=1000,
            help="グッズ購入に使う予定の金額を入力してください")
        food_budget = st.number_input(
            "食事・観光予算（円）",
            min_value=0, value=5000, step=1000,
            help="現地での食事・観光に使う予定の金額を入力してください")
        budget_limit = st.number_input(
            "予算上限（円）※任意",
            min_value=0, value=0, step=5000,
            help="予算の上限を入力すると、計算結果でオーバーの有無を判定します",
        )

if st.button("費用を計算する", type="primary"):
    st.session_state.show_results = True

# 割り勘フォームの操作でも計算結果を表示し続けるため、
# ボタンの戻り値ではなくセッション状態で表示有無を管理する
if st.session_state.get("show_results"):
    st.divider()
    st.subheader("計算結果")

    route = get_transport_options(departure, destination)
    hotel_cost = get_hotel_cost(destination, nights)

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
            "所要時間_分": data["時間"],
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
        f"<strong>{fmt_amount(best['合計'])}</strong>（{num_people}人分）",
        kind="accent",
    )

    if budget_limit > 0:
        if best["合計"] > budget_limit:
            over = best["合計"] - budget_limit
            st.error(f"⚠️ 予算を{fmt_amount(over)}オーバーしています")
        else:
            remain = budget_limit - best["合計"]
            st.success(f"✅ 予算内です（残り{fmt_amount(remain)}）")

    st.subheader("交通手段の比較")
    cheapest_transport = min(results, key=lambda x: x["合計"])["交通手段"]
    fastest_transport = min(
        results, key=lambda x: x["所要時間_分"])["交通手段"]
    for r in results:
        if r["交通手段"] == cheapest_transport:
            badge_text = "💰 最安"
        elif r["交通手段"] == fastest_transport:
            badge_text = "⚡ 最速"
        else:
            badge_text = "⚖️ バランス"
        transport_card(
            r["交通手段"],
            r["交通費（往復）"],
            r["所要時間"],
            r["宿泊費"],
            r["合計"],
            badge_text=badge_text,
            highlight=(r["交通手段"] == cheapest_transport),
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

    # ============================================
    # 宿泊費（じゃらん実勢価格）
    # ============================================
    st.subheader("宿泊費の詳細")
    checkout_date = live_date + datetime.timedelta(days=max(nights, 1))
    hotel_api_result = get_hotel_prices(
        destination,
        live_date.strftime("%Y-%m-%d"),
        checkout_date.strftime("%Y-%m-%d"),
        num_people,
    )

    if hotel_api_result and nights > 0:
        actual_hotel_cost = (
            hotel_api_result["min_price"] * nights * num_people
        )
    else:
        actual_hotel_cost = get_hotel_cost(
            destination, nights
        ) * num_people

    with card():
        if hotel_api_result and nights > 0:
            st.write(
                "じゃらん最安値: "
                f"**{hotel_api_result['min_price']:,}円/泊**"
            )
            st.write(
                f"（{nights}泊 × {num_people}人 = "
                f"**{actual_hotel_cost:,}円**）"
            )
            st.markdown("**おすすめホテル TOP3：**")
            for h in hotel_api_result["hotels"][:3]:
                hcol1, hcol2 = st.columns([4, 1])
                hcol1.write(f"・{h['name']}　{h['price']:,}円/泊")
                hcol2.markdown(f"[予約する →]({h['url']})")
        else:
            st.write(f"概算: {actual_hotel_cost:,}円")
            st.caption("※概算値を表示しています")

    alert(
        f"{num_people}人で行く場合、1人あたり "
        f"<strong>{fmt_amount(best['合計'] // num_people)}</strong>かかります",
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
        departure, destination, live_date, num_people)

    st.markdown("**【ホテルを予約する】**")
    link_row(hotel_links)
    st.caption("※クリックすると外部サイトに移動します")

    st.markdown("**【交通手段を予約する】**")
    link_row(transport_links)
    st.caption("※クリックすると外部サイトに移動します")

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
        placeholder="例：あおい, さくら, はな",
        key="members_input",
        help="一緒に遠征するメンバーの名前をカンマ区切りで入力してください",
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

            if "editing_payment_idx" not in st.session_state:
                st.session_state.editing_payment_idx = None

            if st.session_state.payments:
                st.markdown("**登録済みの支払い**")
                for idx, p in enumerate(st.session_state.payments):
                    if st.session_state.editing_payment_idx == idx:
                        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
                        payer_index = (
                            members.index(p["payer"])
                            if p["payer"] in members else 0
                        )
                        new_payer = c1.selectbox(
                            "支払者", members,
                            index=payer_index,
                            key=f"edit_payer_{idx}",
                        )
                        new_item = c2.text_input(
                            "項目名", value=p["item"],
                            key=f"edit_item_{idx}")
                        new_amount = c3.number_input(
                            "金額（円）", min_value=0, step=100,
                            value=p["amount"], key=f"edit_amount_{idx}")
                        if c4.button("更新", key=f"update_payment_{idx}"):
                            st.session_state.payments[idx] = {
                                "payer": new_payer,
                                "item": new_item,
                                "amount": new_amount,
                            }
                            st.session_state.editing_payment_idx = None
                            st.rerun()
                        if c5.button("キャンセル", key=f"cancel_edit_{idx}"):
                            st.session_state.editing_payment_idx = None
                            st.rerun()
                    else:
                        c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 1, 1])
                        c1.write(p["payer"])
                        c2.write(p["item"])
                        c3.write(f"{p['amount']:,}円")
                        if c4.button("編集", key=f"edit_payment_{idx}"):
                            st.session_state.editing_payment_idx = idx
                            st.rerun()
                        if c5.button("削除", key=f"del_payment_{idx}"):
                            st.session_state.payments.pop(idx)
                            if st.session_state.editing_payment_idx == idx:
                                st.session_state.editing_payment_idx = None
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
    with card():
        st.subheader("💾 この遠征を記録する")
        memo = st.text_area(
            "メモ（自由記入）",
            placeholder="例：アリーナAブロックで神席だった！",
            key="record_memo",
            help="当日の思い出や座席情報などを自由に書き残せます",
        )

        if st.button("📝 記録する", type="primary"):
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
                "hotel_type": DEFAULT_HOTEL_GRADE,
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
                "サイドバーの「マイページ」から確認できます。",
                kind="success",
            )
            st.balloons()
