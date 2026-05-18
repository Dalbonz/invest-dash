import streamlit as st
import json
import os
import pandas as pd

st.set_page_config(
    page_title="Invest Dash",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_engine_output(engine_name: str) -> dict:
    path = os.path.join(os.path.dirname(__file__), f"engines/{engine_name}/output.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

with st.sidebar:
    st.title("📈 Invest Dash")
    st.markdown("---")
    page = st.radio("메뉴", ["🏠 대시보드", "💼 포트폴리오", "🌐 시장", "🤖 AI 요약", "⚙️ 설정"])

if page == "🏠 대시보드":
    st.title("대시보드")
    col1, col2, col3 = st.columns(3)
    market = load_engine_output("market")
    ai = load_engine_output("ai_summary")
    portfolio = load_engine_output("portfolio")
    scores = market.get("data", {}).get("scores", {})
    port_data = portfolio.get("data", {})

    with col1:
        st.metric("KR 시장 점수", scores.get("kr", "-"))
    with col2:
        st.metric("US 시장 점수", scores.get("us", "-"))
    with col3:
        risk = market.get("data", {}).get("risk_level", "-")
        st.metric("리스크 레벨", f"Lv.{risk}")

    st.markdown("---")
    col4, col5 = st.columns(2)
    with col4:
        total = port_data.get("total_value_krw", 0)
        st.metric("주식 평가금액", f"{total:,.0f}원" if total else "-")
    with col5:
        profit = port_data.get("total_profit_krw", 0)
        st.metric("총 수익", f"{profit:,.0f}원" if profit else "-")

    st.markdown("---")
    st.subheader("🤖 AI 요약")
    ai_data = ai.get("data", {})
    if ai_data:
        st.info(ai_data.get("market_summary", "데이터 없음"))
        for s in ai_data.get("key_signals", []):
            st.markdown(f"- {s}")
    else:
        st.warning("AI 요약 데이터 없음 - 엔진을 실행해주세요.")

elif page == "💼 포트폴리오":
    st.title("포트폴리오")
    from shared.gsheet_client import read_sheet

    sheet_data = read_sheet("주식현황상세")
    if sheet_data:
        df = pd.DataFrame(sheet_data)
        # 빈 행 제거
        df = df[df["종목명"].notna() & (df["종목명"] != "")]
        st.dataframe(df, use_container_width=True)

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            if "평가총액(원)" in df.columns:
                total = pd.to_numeric(df["평가총액(원)"], errors="coerce").sum()
                st.metric("총 평가금액", f"{total:,.0f}원")
        with col2:
            if "원화수익" in df.columns:
                profit = pd.to_numeric(df["원화수익"], errors="coerce").sum()
                st.metric("총 수익", f"{profit:,.0f}원")
    else:
        st.warning("시트 연결 실패 또는 데이터 없음")

elif page == "🌐 시장":
    st.title("시장 현황")
    market = load_engine_output("market")
    raw = market.get("data", {}).get("raw_summary", {})
    if raw:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🇰🇷 KR")
            st.json(raw.get("kr", {}))
        with col2:
            st.subheader("🇺🇸 US")
            st.json(raw.get("us", {}))
    else:
        st.warning("시장 데이터 없음 - 엔진을 실행해주세요.")

elif page == "🤖 AI 요약":
    st.title("AI 시장 해석")
    ai = load_engine_output("ai_summary")
    data = ai.get("data", {})
    if data:
        st.metric("리스크 레벨", data.get("risk_level", "-"))
        st.markdown(f"**시장 요약:** {data.get('market_summary', '')}")
        st.markdown(f"**액션 힌트:** {data.get('action_hint', '')}")
        st.markdown(f"**포트폴리오:** {data.get('portfolio_comment', '')}")
    else:
        st.warning("AI 데이터 없음 - 엔진을 실행해주세요.")

elif page == "⚙️ 설정":
    st.title("설정")
    st.info("API 키 및 환경변수는 Streamlit Cloud Secrets에서 관리하세요.")
    st.code("""
ANTHROPIC_API_KEY = "sk-ant-..."
GOOGLE_SHEETS_ID = "..."
GOOGLE_SERVICE_ACCOUNT_JSON = '{"type":"service_account",...}'
    """)