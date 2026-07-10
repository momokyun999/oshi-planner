
import collections
import datetime
import os
import sys

import plotly.graph_objects as go
import streamlit as st

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.calculator import calculate_split
from utils.data import hotel_costs, transport_data
from utils.sidebar import render_sidebar
from utils.storage import delete_record, load_records, update_record
from utils.styles import alert, card, inject_theme

st.set_page_config(
    page_title="マイページ | 推し活遠征プランナー",
    page_icon="📖",
    layout="wide",
)

inject_theme()
render_sidebar()

st.title("マイページ")
st.caption("これまでの遠征記録を振り返ることができます")

st.divider()

records = load_records()

if "editing_id" not in st.session_state:
    st.session_state.editing_id = None
if "mypage_edit_payments" not in st.session_state:
    st.session_state.mypage_edit_payments = []
if "mypage_editing_payment_idx" not in st.session_state:
    st.session_state.mypage_editing_payment_idx = None
if "mypage_edit_split_result" not in st.session_state:
    st.session_state.mypage_edit_split_result = None

if not records:
    alert(
        "まだ記録がありません。"
        "遠征プランナーで費用を計算し、"
        "「この遠征を記録する」から記録を保存してください。",
        kind="accent",
    )
    st.stop()

# ============================================
# 詳細ページ
# ============================================
selected_id = st.session_state.get("mypage_selected_id")

if selected_id:
    record = next(
        (r for r in records if r["id"] == selected_id), None)

    if st.button("← 一覧に戻る"):
        st.session_state.mypage_selected_id = None
        st.rerun()

    if record is None:
        alert("記録が見つかりませんでした。", kind="warning")
        st.stop()

    with card():
        st.subheader("【遠征詳細】")
        st.write(f"日程: {record['live_date']}")
        st.write(
            f"会場: {record['venue']}（{record['destination']}）")
        st.write(
            f"経路: {record['departure']} → {record['destination']}"
            f" / {record['transport']}"
        )
        members = record.get("members", [])
        st.write(
            "メンバー: "
            + (", ".join(members) if members else "（未登録）")
        )

        st.markdown("**費用内訳:**")
        nights = record.get("nights", 0)
        num_people = record.get("num_people", 1)
        ticket_total = record.get("ticket_price", 0) * num_people
        st.write(f"　交通費（往復）: {record.get('transport_cost', 0):,}円")
        st.write(f"　宿泊費: {record.get('hotel_cost', 0):,}円")
        st.write(f"　チケット代: {ticket_total:,}円")
        st.write(f"　グッズ: {record.get('goods_budget', 0):,}円")
        st.write(f"　食事・観光: {record.get('food_budget', 0):,}円")
        st.write(f"　合計: {record.get('total_cost', 0):,}円")
        if num_people:
            st.write(
                "　1人あたり: "
                f"{record.get('total_cost', 0) // num_people:,}円"
            )

        payments = record.get("payments", [])
        if payments:
            st.markdown("**支払い一覧:**")
            for p in payments:
                st.write(
                    f"　{p['payer']}: {p['item']} {p['amount']:,}円"
                )

        settlement = record.get("settlement", [])
        st.markdown("**割り勘精算:**")
        if settlement:
            for s in settlement:
                st.write(f"　{s['from']} → {s['to']} に {s['amount']:,}円")
        else:
            st.write("　精算記録はありません。")

        if record.get("memo"):
            st.markdown("**メモ:**")
            st.write(record["memo"])

    st.divider()
    if st.button("この記録を削除する"):
        delete_record(record["id"])
        st.session_state.mypage_selected_id = None
        st.rerun()

    st.stop()

# ============================================
# 進行中の遠征（当日の割り勘記入）
# ============================================
today = datetime.date.today()


def _is_ongoing(r):
    try:
        start = datetime.date.fromisoformat(r["live_date"])
    except (KeyError, ValueError):
        return False
    end = start + datetime.timedelta(days=r.get("nights", 0))
    return start <= today <= end


ongoing_records = [r for r in records if _is_ongoing(r)]

if ongoing_records:
    st.subheader("🔴 進行中の遠征")
    st.caption("当日の支払いをその場で記録できます")

    for record in ongoing_records:
        rid = record["id"]
        members = record.get("members", [])
        with card():
            st.markdown(
                f"**{record.get('live_date', '')} "
                f"{record.get('venue', '')}**"
            )

            if not members:
                st.caption(
                    "メンバーが未登録です。"
                    "一覧の「編集」からメンバーを追加してください。"
                )
                continue

            with st.form(
                    f"ongoing_payment_form_{rid}", clear_on_submit=True):
                pc1, pc2, pc3, pc4 = st.columns([2, 2, 2, 1])
                payer = pc1.selectbox("支払者", members)
                item = pc2.text_input("項目名", placeholder="例：グッズ")
                amount = pc3.number_input(
                    "金額（円）", min_value=0, step=100)
                submitted = pc4.form_submit_button("追加")
                if submitted and item and amount > 0:
                    payments = record.get("payments", []) + [{
                        "payer": payer,
                        "item": item,
                        "amount": amount,
                    }]
                    settlement = calculate_split(
                        members, payments)["settlement"]
                    update_record(rid, {
                        **record,
                        "payments": payments,
                        "settlement": settlement,
                    })
                    st.rerun()

            payments = record.get("payments", [])
            if payments:
                st.markdown("**本日までの支払い**")
                for idx, p in enumerate(payments):
                    pcol1, pcol2, pcol3, pcol4 = st.columns([2, 2, 2, 1])
                    pcol1.write(p["payer"])
                    pcol2.write(p["item"])
                    pcol3.write(f"{p['amount']:,}円")
                    if pcol4.button(
                            "削除", key=f"ongoing_del_{rid}_{idx}"):
                        new_payments = (
                            payments[:idx] + payments[idx + 1:]
                        )
                        settlement = calculate_split(
                            members, new_payments)["settlement"]
                        update_record(rid, {
                            **record,
                            "payments": new_payments,
                            "settlement": settlement,
                        })
                        st.rerun()

                split_result = calculate_split(members, payments)
                st.write(
                    "1人あたりの負担額: "
                    f"**{split_result['per_person']:,.0f}円**"
                )

    st.divider()

# ============================================
# サマリーカード
# ============================================
total_trips = len(records)
total_cost = sum(r.get("total_cost", 0) for r in records)
destinations = [r.get("destination") for r in records if r.get("destination")]
most_common_destination = (
    collections.Counter(destinations).most_common(1)[0][0]
    if destinations else "―"
)

col1, col2, col3 = st.columns(3)
with col1:
    with card():
        st.metric("遠征回数", f"{total_trips}回")
with col2:
    with card():
        st.metric("総遠征費用", f"{total_cost:,}円")
with col3:
    with card():
        st.metric("最多訪問地", most_common_destination)

st.divider()

# ============================================
# 遠征履歴一覧（新しい順）
# ============================================
st.subheader("遠征履歴一覧")

sorted_records = sorted(
    records,
    key=lambda r: (r.get("live_date", ""), r.get("created_at", "")),
    reverse=True,
)

for record in sorted_records:
    rid = record["id"]
    with card():
        st.markdown(
            f"**{record.get('live_date', '')} "
            f"{record.get('venue', '')}**"
        )
        nights = record.get("nights", 0)
        st.write(
            f"{record.get('departure', '')} → "
            f"{record.get('destination', '')} / "
            f"{record.get('transport', '')} / "
            f"{nights}泊{nights + 1}日 / "
            f"{record.get('num_people', 1)}人"
        )
        st.write(f"合計: {record.get('total_cost', 0):,}円")

        b1, b2, b3 = st.columns([1, 1, 1])
        if b1.button("詳細を見る", key=f"detail_{rid}"):
            st.session_state.mypage_selected_id = rid
            st.rerun()
        if b2.button("編集", key=f"edit_{rid}"):
            st.session_state.editing_id = rid
            st.session_state["mypage_edit_live_date"] = (
                datetime.date.fromisoformat(record["live_date"])
            )
            st.session_state["mypage_edit_venue"] = record.get("venue", "")
            st.session_state["mypage_edit_transport"] = record.get(
                "transport", "新幹線")
            st.session_state["mypage_edit_nights"] = record.get(
                "nights", 0)
            st.session_state["mypage_edit_num_people"] = record.get(
                "num_people", 1)
            st.session_state["mypage_edit_ticket_price"] = record.get(
                "ticket_price", 0)
            st.session_state["mypage_edit_goods_budget"] = record.get(
                "goods_budget", 0)
            st.session_state["mypage_edit_food_budget"] = record.get(
                "food_budget", 0)
            st.session_state["mypage_edit_memo"] = record.get("memo", "")
            st.session_state["mypage_edit_members_input"] = ", ".join(
                record.get("members", []))
            st.session_state.mypage_edit_payments = [
                dict(p) for p in record.get("payments", [])
            ]
            st.session_state.mypage_editing_payment_idx = None
            st.session_state.mypage_edit_split_result = None
            st.rerun()
        if b3.button("削除", key=f"delete_{rid}"):
            delete_record(rid)
            if st.session_state.editing_id == rid:
                st.session_state.editing_id = None
            st.rerun()

        if st.session_state.editing_id == rid:
            st.divider()
            st.markdown("**遠征記録を編集**")

            st.date_input("ライブ日程", key="mypage_edit_live_date")
            st.text_input("会場名", key="mypage_edit_venue")

            transport_options = list(
                transport_data.get(
                    (record["departure"], record["destination"]), {}
                ).keys()
            ) or ["新幹線", "高速バス", "飛行機"]
            st.selectbox(
                "交通手段", transport_options, key="mypage_edit_transport")

            e1, e2 = st.columns(2)
            e1.number_input(
                "宿泊数", min_value=0, max_value=7,
                key="mypage_edit_nights")
            e2.number_input(
                "人数", min_value=1, max_value=10,
                key="mypage_edit_num_people")

            e3, e4, e5 = st.columns(3)
            e3.number_input(
                "チケット代（円）", min_value=0, step=500,
                key="mypage_edit_ticket_price")
            e4.number_input(
                "グッズ予算（円）", min_value=0, step=1000,
                key="mypage_edit_goods_budget")
            e5.number_input(
                "食事・観光予算（円）", min_value=0, step=1000,
                key="mypage_edit_food_budget")

            st.text_area("メモ（自由記入）", key="mypage_edit_memo")

            st.markdown("**メンバー・割り勘計算**")
            st.text_input(
                "メンバー名を入力（カンマ区切り）",
                key="mypage_edit_members_input",
            )
            edit_members = [
                m.strip()
                for m in
                st.session_state.mypage_edit_members_input.split(",")
                if m.strip()
            ]

            if edit_members:
                with st.form(
                        f"mypage_payment_form_{rid}", clear_on_submit=True):
                    pcol1, pcol2, pcol3, pcol4 = st.columns([2, 2, 2, 1])
                    payer = pcol1.selectbox("支払者", edit_members)
                    item = pcol2.text_input(
                        "項目名", placeholder="例：交通費")
                    amount = pcol3.number_input(
                        "金額（円）", min_value=0, step=100)
                    submitted = pcol4.form_submit_button("追加")
                    if submitted and item and amount > 0:
                        st.session_state.mypage_edit_payments.append({
                            "payer": payer,
                            "item": item,
                            "amount": amount,
                        })

                if st.session_state.mypage_edit_payments:
                    st.markdown("**登録済みの支払い**")
                    for idx, p in enumerate(
                            st.session_state.mypage_edit_payments):
                        if (st.session_state.mypage_editing_payment_idx
                                == idx):
                            c1, c2, c3, c4, c5 = st.columns(
                                [2, 2, 2, 1, 1])
                            payer_index = (
                                edit_members.index(p["payer"])
                                if p["payer"] in edit_members else 0
                            )
                            new_payer = c1.selectbox(
                                "支払者", edit_members,
                                index=payer_index,
                                key=f"mypage_edit_payer_{rid}_{idx}",
                            )
                            new_item = c2.text_input(
                                "項目名", value=p["item"],
                                key=f"mypage_edit_item_{rid}_{idx}")
                            new_amount = c3.number_input(
                                "金額（円）", min_value=0, step=100,
                                value=p["amount"],
                                key=f"mypage_edit_amount_{rid}_{idx}")
                            if c4.button(
                                    "更新",
                                    key=f"mypage_update_payment_{rid}_{idx}"):
                                st.session_state.mypage_edit_payments[idx] = {
                                    "payer": new_payer,
                                    "item": new_item,
                                    "amount": new_amount,
                                }
                                st.session_state.mypage_editing_payment_idx = (
                                    None
                                )
                                st.rerun()
                            if c5.button(
                                    "キャンセル",
                                    key=f"mypage_cancel_payment_{rid}_{idx}"):
                                st.session_state.mypage_editing_payment_idx = (
                                    None
                                )
                                st.rerun()
                        else:
                            c1, c2, c3, c4, c5 = st.columns(
                                [2, 2, 2, 1, 1])
                            c1.write(p["payer"])
                            c2.write(p["item"])
                            c3.write(f"{p['amount']:,}円")
                            if c4.button(
                                    "編集",
                                    key=f"mypage_edit_payment_{rid}_{idx}"):
                                st.session_state.mypage_editing_payment_idx = (
                                    idx
                                )
                                st.rerun()
                            if c5.button(
                                    "削除",
                                    key=f"mypage_del_payment_{rid}_{idx}"):
                                st.session_state.mypage_edit_payments.pop(
                                    idx)
                                if (st.session_state
                                        .mypage_editing_payment_idx == idx):
                                    st.session_state \
                                        .mypage_editing_payment_idx = None
                                st.rerun()

            if st.button("再計算", key=f"mypage_recalc_{rid}"):
                if edit_members and st.session_state.mypage_edit_payments:
                    st.session_state.mypage_edit_split_result = (
                        calculate_split(
                            edit_members,
                            st.session_state.mypage_edit_payments,
                        )
                    )
                else:
                    st.session_state.mypage_edit_split_result = None

            if st.session_state.mypage_edit_split_result:
                sr = st.session_state.mypage_edit_split_result
                st.write(
                    "1人あたりの負担額: "
                    f"**{sr['per_person']:,.0f}円**"
                )
                if sr["settlement"]:
                    for s in sr["settlement"]:
                        st.write(
                            f"{s['from']} → {s['to']} に "
                            f"{s['amount']:,}円"
                        )
                else:
                    st.write(
                        "精算の必要はありません"
                        "（全員の負担額が同じです）"
                    )

            s1, s2 = st.columns(2)
            if s1.button("保存", key=f"mypage_save_{rid}", type="primary"):
                new_transport = st.session_state.mypage_edit_transport
                new_nights = st.session_state.mypage_edit_nights
                new_num_people = st.session_state.mypage_edit_num_people
                new_ticket_price = st.session_state.mypage_edit_ticket_price
                new_goods_budget = st.session_state.mypage_edit_goods_budget
                new_food_budget = st.session_state.mypage_edit_food_budget

                fare = transport_data.get(
                    (record["departure"], record["destination"]), {}
                ).get(new_transport, {}).get("料金", 0)
                hotel_rate = hotel_costs.get(
                    record["destination"], {}
                ).get(record.get("hotel_type", "ビジネス"), 0)

                transport_cost = fare * 2 * new_num_people
                hotel_cost = hotel_rate * new_nights * new_num_people
                total_cost = (
                    transport_cost
                    + hotel_cost
                    + new_ticket_price * new_num_people
                    + new_goods_budget
                    + new_food_budget
                )

                split_result = None
                if edit_members and st.session_state.mypage_edit_payments:
                    split_result = calculate_split(
                        edit_members, st.session_state.mypage_edit_payments)

                updated_record = {
                    **record,
                    "live_date": st.session_state[
                        "mypage_edit_live_date"].isoformat(),
                    "venue": st.session_state["mypage_edit_venue"],
                    "transport": new_transport,
                    "transport_cost": transport_cost,
                    "hotel_cost": hotel_cost,
                    "nights": new_nights,
                    "num_people": new_num_people,
                    "ticket_price": new_ticket_price,
                    "goods_budget": new_goods_budget,
                    "food_budget": new_food_budget,
                    "total_cost": total_cost,
                    "members": edit_members,
                    "payments": st.session_state.mypage_edit_payments,
                    "settlement": (
                        split_result["settlement"] if split_result else []
                    ),
                    "memo": st.session_state["mypage_edit_memo"],
                }
                update_record(rid, updated_record)
                st.session_state.editing_id = None
                st.rerun()

            if s2.button("キャンセル", key=f"mypage_cancel_{rid}"):
                st.session_state.editing_id = None
                st.rerun()

st.divider()

# ============================================
# 遠征費用の推移（月別）
# ============================================
st.subheader("遠征費用の推移")

monthly = collections.defaultdict(int)
for r in records:
    live_date = r.get("live_date", "")
    if len(live_date) >= 7:
        monthly[live_date[:7]] += r.get("total_cost", 0)

if monthly:
    sorted_months = sorted(monthly.keys())
    with card():
        fig = go.Figure(go.Scatter(
            x=sorted_months,
            y=[monthly[m] for m in sorted_months],
            mode="lines+markers",
            line=dict(color="#6366F1", width=3),
            marker=dict(color="#6366F1", size=8),
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("データがありません。")

st.divider()

# ============================================
# 訪問都市マップ（訪問回数）
# ============================================
st.subheader("訪問都市マップ")

city_counts = collections.Counter(destinations)
if city_counts:
    with card():
        fig = go.Figure(go.Bar(
            x=list(city_counts.keys()),
            y=list(city_counts.values()),
            marker_color="#6366F1",
        ))
        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
            height=280,
            margin=dict(l=0, r=0, t=10, b=0),
        )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=True, gridcolor="#E5E7EB")
        st.plotly_chart(fig, use_container_width=True)
else:
    st.write("データがありません。")
