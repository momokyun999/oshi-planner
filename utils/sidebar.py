"""
全ページ共通のサイドバー。
ナビゲーション・遠征サマリー・表示設定・アプリ情報を表示する。
"""

import datetime

import streamlit as st

from utils.storage import load_records


def render_sidebar():
    st.sidebar.markdown("## 🎤 推し活遠征プランナー")

    st.sidebar.page_link(
        "oshi_planner.py", label="遠征を計算する", icon="📍")
    st.sidebar.page_link(
        "pages/mypage.py", label="マイページ", icon="📋")

    # ------ 遠征サマリー ------
    st.sidebar.divider()
    st.sidebar.subheader("📊 遠征サマリー")

    records = load_records()
    total_trips = len(records)
    total_cost = sum(r.get("total_cost", 0) for r in records)

    now = datetime.datetime.now()
    this_month = sum(
        1 for r in records
        if r.get("live_date", "").startswith(now.strftime("%Y-%m"))
    )

    st.sidebar.metric("累計遠征回数", f"{total_trips}回")
    st.sidebar.metric("累計費用", f"{total_cost:,}円")
    st.sidebar.metric("今月の遠征", f"{this_month}回")

    # ------ 表示設定 ------
    st.sidebar.divider()
    st.sidebar.subheader("⚙️ 表示設定")

    st.sidebar.checkbox(
        "通貨表示（円）を表示",
        value=st.session_state.get("show_currency", True),
        key="show_currency",
        help="金額の末尾に「円」を表示するかどうかを切り替えます",
    )
    st.sidebar.checkbox(
        "繁忙期警告を表示",
        value=st.session_state.get("show_busy_warning", True),
        key="show_busy_warning",
        help="年末年始・GW・お盆など繁忙期の警告表示を切り替えます",
    )

    # ------ このアプリについて ------
    st.sidebar.divider()
    with st.sidebar.expander("ℹ️ このアプリについて"):
        st.write(
            "推し活の遠征費用をまとめて計算できるツールです。"
            "交通費・宿泊費・グッズ代を計算し、"
            "複数人での割り勘も自動精算できます。"
        )
        st.caption("Version 1.0")
