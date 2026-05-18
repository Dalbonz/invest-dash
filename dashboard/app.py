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
    path = os.path.join(os.path.dirname(__file__), f"../engines/{engine_name}/output.json")
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

with st.sidebar:
    st.title("📈 Invest Dash")
    st.markdown("---")
    page = st.radio("메뉴", ["🏠 대시보드", "💼 포트폴리오", "🌐 시장", "🤖 AI 요약", "⚙️ 설정"])
    st.markdown("---")
    if st.button("🔄 엔진 새로고침"):
        st.info("엔진 실행은 Claude Code에서 수동 실행해주세요.")

if page == "🏠 대시보드":
    st.title("대시보드")
    col1, col2, col3 = st.columns(3)

    market = load_engine_output("market")
    ai = load_engine_output("ai_summary")

    scores = market.get("data", {}).get("scores", {})
    with col1:
        st.metric("KR 시장 점수", scores.get("kr", "-"))
    with col2:
        st.metric("US 시장 점수", scores.get("us", "-"))
    with col3:
        risk = market.get("data", {}).get("risk_level", "-")
        st.metric("리스크 레벨", f"Lv.{risk}")

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
    from shared.gsheet_client import read_sheet, write_sheet

    sheet_data = read_sheet("holdings")
    if sheet_data:
        df = pd.DataFrame(sheet_data)
        edited = st.data_editor(df, num_rows="dynamic", use_container_width=True)
        if st.button("💾 저장"):
            if write_sheet("holdings", edited.to_dict("records")):
                st.success("저장 완료!")
            else:
                st.error("저장 실패")
    else:
        st.warning("Holdings 시트가 비어있거나 연결 실패")

elif page == "🌐 시장":
    st.title("시장 현황")
    market = load_engine_output("market")
    raw = market.get("data", {}).get("raw_summary", {})
    if raw:
        st.subheader("KR 지수")
        st.json(raw.get("kr", {}))
        st.subheader("US 지수")
        st.json(raw.get("us", {}))
    else:
        st.warning("시장 데이터 없음")

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
        st.warning("AI 데이터 없음")

elif page == "⚙️ 설정":
    st.title("설정")
    st.info("API 키 및 환경변수는 Streamlit Cloud Secrets에서 관리하세요.")
    st.code("""
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_SHEETS_ID=...
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
    """)