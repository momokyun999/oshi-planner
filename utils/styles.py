"""
アプリ全体の見た目（フォント・カラー・カード等）を定義する。
将来：ブランドカラーの変更等はこのファイルだけ差し替えればよい
"""

from contextlib import contextmanager

import streamlit as st

COLOR_BG = "#FAFAFA"
COLOR_TEXT = "#1A1A1A"
COLOR_SUBTEXT = "#6B7280"
COLOR_ACCENT = "#6366F1"
COLOR_ACCENT_HOVER = "#4F46E5"
COLOR_SUCCESS = "#10B981"
COLOR_WARNING = "#F59E0B"
COLOR_CARD_BG = "#FFFFFF"
COLOR_BORDER = "#E5E7EB"
COLOR_LINK_BG = "#F3F4F6"

_THEME_CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Klee+One&family=Inter:wght@300;400;600&display=swap');

html, body, [class*="css"] {{
    font-family: 'Inter', 'Noto Sans JP', sans-serif;
}}

h1, h2, h3 {{
    font-family: 'Klee One', cursive !important;
    font-weight: 600 !important;
}}

h1 {{
    font-size: 2.4rem !important;
}}

[data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background-color: {COLOR_BG};
}}

[data-testid="stMainBlockContainer"] {{
    color: {COLOR_TEXT};
}}

hr {{
    border: none !important;
    border-top: 1px solid {COLOR_BORDER} !important;
    margin: 20px 0 !important;
}}

/* ------ カード（:has() マーカー方式） ------ */
div[data-testid="stVerticalBlock"]:has(> div[data-testid="stElementContainer"] span.oshi-card-marker) {{
    background: {COLOR_CARD_BG};
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 16px;
}}

/* ------ ボタン ------ */
.stButton > button {{
    background-color: {COLOR_ACCENT};
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-size: 16px;
    font-weight: 600;
    width: 100%;
    transition: background 0.2s;
}}
.stButton > button:hover {{
    background-color: {COLOR_ACCENT_HOVER};
    color: white;
}}
.stButton > button p {{
    font-weight: 600;
}}

/* ------ サイドバー ------ */
[data-testid="stSidebar"] {{
    background-color: #F9FAFB;
    border-right: 1px solid {COLOR_BORDER};
}}
[data-testid="stSidebar"] a {{
    font-family: 'Klee One', cursive;
    font-size: 16px;
    color: {COLOR_TEXT};
}}
/* 自動生成のページナビゲーションは非表示にし、
   utils/sidebar.py のカスタムナビゲーションに置き換える */
[data-testid="stSidebarNav"] {{
    display: none;
}}

/* ------ st.metric ------ */
[data-testid="stMetricValue"] {{
    font-size: 2rem;
    font-weight: 700;
    color: {COLOR_TEXT};
}}
[data-testid="stMetricLabel"] {{
    color: {COLOR_SUBTEXT};
}}

/* ------ 交通手段の比較カード ------ */
.oshi-transport-card {{
    background: {COLOR_CARD_BG};
    border-radius: 12px;
    padding: 18px 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 12px;
}}
.oshi-transport-card.best {{
    border-left: 4px solid {COLOR_ACCENT};
}}
.oshi-transport-header {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}}
.oshi-transport-name {{
    font-family: 'Klee One', cursive;
    font-size: 18px;
    font-weight: 600;
    color: {COLOR_TEXT};
}}
.oshi-best-badge {{
    color: {COLOR_ACCENT};
    font-size: 13px;
    font-weight: 600;
}}
.oshi-transport-row {{
    display: flex;
    justify-content: space-between;
    padding: 3px 0;
    color: {COLOR_SUBTEXT};
    font-size: 14px;
}}
.oshi-transport-row.total {{
    color: {COLOR_TEXT};
    font-weight: 600;
    font-size: 16px;
    border-top: 1px solid {COLOR_BORDER};
    margin-top: 6px;
    padding-top: 8px;
}}

/* ------ 予約リンク ------ */
.oshi-link-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
    margin-bottom: 8px;
}}
a.oshi-link, a.oshi-link:visited {{
    display: inline-block;
    padding: 8px 16px;
    background: {COLOR_LINK_BG};
    color: {COLOR_TEXT} !important;
    border-radius: 6px;
    text-decoration: none !important;
    font-size: 14px;
    border: 1px solid {COLOR_BORDER};
    transition: background 0.2s;
}}
a.oshi-link:hover {{
    background: {COLOR_BORDER};
    text-decoration: none !important;
}}

/* ------ アラート（成功・警告） ------ */
.oshi-alert {{
    padding: 12px 16px;
    border-radius: 8px;
    margin: 12px 0;
    font-size: 14px;
    color: {COLOR_TEXT};
}}
</style>
"""


def inject_theme():
    st.markdown(_THEME_CSS, unsafe_allow_html=True)


@contextmanager
def card():
    """白背景・角丸・薄い影のカードでラップするコンテナ"""
    with st.container():
        st.markdown(
            '<span class="oshi-card-marker"></span>',
            unsafe_allow_html=True,
        )
        yield


def alert(message, kind="accent"):
    """絵文字を使わない、色分けだけで状態を伝えるアラート表示"""
    colors = {
        "success": COLOR_SUCCESS,
        "warning": COLOR_WARNING,
        "accent": COLOR_ACCENT,
    }
    color = colors.get(kind, COLOR_ACCENT)
    st.markdown(
        f'<div class="oshi-alert" style="'
        f'background:{color}1A; border-left:4px solid {color};">'
        f'{message}</div>',
        unsafe_allow_html=True,
    )


def link_row(links):
    """
    予約リンクを横並びのHTMLの<a>タグとして表示する。
    st.link_button はStreamlit Cloud上で正しく機能しないことがあるため、
    st.markdown + unsafe_allow_html でリンクを直接出力する。
    """
    html = "".join(
        f'<a href="{url}" target="_blank" '
        f'rel="noopener noreferrer" '
        f'style="display:inline-block; padding:8px 16px; '
        f'background:{COLOR_LINK_BG}; color:{COLOR_TEXT}; '
        f'border-radius:6px; text-decoration:none; '
        f'font-size:14px; margin:4px 4px 4px 0; '
        f'border:1px solid {COLOR_BORDER};">'
        f'{name} →</a>'
        for name, url in links.items()
    )
    st.markdown(
        f'<div style="display:flex; flex-wrap:wrap;">{html}</div>',
        unsafe_allow_html=True,
    )


def transport_card(
        name, transport_cost, duration, hotel_cost, total,
        badge_text="", highlight=False):
    """交通手段の比較を表すカスタムHTMLカード"""
    badge = (
        f'<span class="oshi-best-badge">{badge_text}</span>'
        if badge_text else ""
    )
    css_class = "oshi-transport-card best" if highlight else "oshi-transport-card"
    html = (
        f'<div class="{css_class}">'
        f'<div class="oshi-transport-header">'
        f'<span class="oshi-transport-name">{name}</span>{badge}'
        f'</div>'
        f'<div class="oshi-transport-row">'
        f'<span>交通費（往復）</span><span>{transport_cost:,}円</span></div>'
        f'<div class="oshi-transport-row">'
        f'<span>所要時間</span><span>{duration}</span></div>'
        f'<div class="oshi-transport-row">'
        f'<span>宿泊費</span><span>{hotel_cost:,}円</span></div>'
        f'<div class="oshi-transport-row total">'
        f'<span>合計</span><span>{total:,}円</span></div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
