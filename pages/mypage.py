
import collections
import os
import sys

import pandas as pd
import streamlit as st

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.storage import delete_record, load_records

st.set_page_config(
    page_title="マイページ | 推し活遠征プランナー",
    page_icon="📖",
    layout="wide",
)

st.title("📖 マイページ")
st.caption("これまでの遠征記録を振り返ることができます")

st.divider()

records = load_records()

if not records:
    st.info(
        "まだ記録がありません。"
        "遠征プランナーで費用を計算し、"
        "「この遠征を記録する」から記録を保存してください。"
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
        st.warning("記録が見つかりませんでした。")
        st.stop()

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
    if st.button("🗑️ この記録を削除する"):
        delete_record(record["id"])
        st.session_state.mypage_selected_id = None
        st.rerun()

    st.stop()

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

card1, card2, card3 = st.columns(3)
card1.metric("遠征回数", f"{total_trips}回")
card2.metric("総遠征費用", f"{total_cost:,}円")
card3.metric("最多訪問地", most_common_destination)

st.divider()

# ============================================
# 遠征履歴一覧（新しい順）
# ============================================
st.subheader("📅 遠征履歴一覧")

sorted_records = sorted(
    records,
    key=lambda r: (r.get("live_date", ""), r.get("created_at", "")),
    reverse=True,
)

for record in sorted_records:
    with st.container(border=True):
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

        b1, b2 = st.columns([1, 1])
        if b1.button("詳細を見る", key=f"detail_{record['id']}"):
            st.session_state.mypage_selected_id = record["id"]
            st.rerun()
        if b2.button("削除", key=f"delete_{record['id']}"):
            delete_record(record["id"])
            st.rerun()

st.divider()

# ============================================
# 遠征費用の推移（月別）
# ============================================
st.subheader("📈 遠征費用の推移")

monthly = collections.defaultdict(int)
for r in records:
    live_date = r.get("live_date", "")
    if len(live_date) >= 7:
        monthly[live_date[:7]] += r.get("total_cost", 0)

if monthly:
    sorted_months = sorted(monthly.keys())
    monthly_df = pd.DataFrame(
        {"費用": [monthly[m] for m in sorted_months]},
        index=sorted_months,
    )
    st.line_chart(monthly_df)
else:
    st.write("データがありません。")

st.divider()

# ============================================
# 訪問都市マップ（訪問回数）
# ============================================
st.subheader("🗺️ 訪問都市マップ")

city_counts = collections.Counter(destinations)
if city_counts:
    city_df = pd.DataFrame(
        {"訪問回数": list(city_counts.values())},
        index=list(city_counts.keys()),
    )
    st.bar_chart(city_df)
else:
    st.write("データがありません。")
