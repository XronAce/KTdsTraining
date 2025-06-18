import logging

import streamlit as st
from dotenv import load_dotenv
from streamlit_js_eval import get_geolocation

# Load from environment variables
load_dotenv()

import auth.google_auth as google_auth
import services.azure_agent as azure_agent
import services.google_calendar as google_calendar
import services.kakao_api as kakao_api
import services.ktds_calendar as ktds_calendar
import utils.formatter as formatter
import components


# --- Configure logging ---
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Streamlit Setup ---
st.set_page_config(page_title="AI Morning Briefing", layout="wide")

col_left, col_right = st.columns([9, 1])

with col_left:
    st.title("☀️ AI 모닝 브리핑")

with col_right:
    if "google_token" not in st.session_state:
        if st.query_params.get("code"):
            google_auth.exchange_token()
        else:
            auth_url = google_auth.get_authorization_url()
            components.google_login_button(auth_url)
    else:
        st.button("로그아웃", on_click=lambda: st.logout(), type="primary")

if "google_token" not in st.session_state:
    st.info("서비스를 이용하기 위해선 **Google 계정**으로 **로그인**이 필요합니다.")
else:
    st.success("구글 계정 로그인 완료 ✅")
    with st.status("사용자 위치 정보 확인중...", expanded=True) as status:
        location = get_geolocation()
        lat, lon = None, None
        if location:
            status.update(label="위치 정보 확인 완료(GPS)", state="complete")
            lat, lon = location['coords']['latitude'], location['coords']['longitude']
        else:
            address_input = st.text_input("🏡 현재 주소를 입력하세요 (예: 서울시 서초구 효령로 176)", placeholder="주소 입력")

            if address_input:
                status.update(label="위치 정보 확인 완료(Kakao 좌표 조회)", state="complete")
                lat, lon = kakao_api.get_coordinates_from_kakao(address_input)

        if lat and lon:
            st.success(f"🏡 현재 위치: {kakao_api.get_korean_road_address(lat, lon)} (좌표: {lat:.3f}, {lon:.3f})")
        else:
            status.update(label="위치 정보 습득 실패", state="complete")

    if lat and lon:
        all_events = []

        use_ktds = st.sidebar.radio(
            "캘린더 연동 선택",
            ("연동 안함", "KTds 캘린더 연동하기"),
            index=0
        ) == "KTds 캘린더 연동하기"

        # Reset calendar fetch state when checkbox toggles
        if "calendar_fetched" not in st.session_state or st.session_state.get("ktds_enabled") != use_ktds:
            st.session_state["calendar_fetched"] = False
            st.session_state["ktds_enabled"] = use_ktds
            st.session_state["calendar_data"] = []

        if use_ktds:
            if not st.session_state["calendar_fetched"]:
                with st.sidebar.form("ktds_login_form"):
                    ktds_username = st.text_input("KTds 이메일 주소 (예: hong_gil.dong@kt.com)")
                    ktds_password = st.text_input("비밀번호", type="password")
                    submitted = st.form_submit_button("캘린더 불러오기")

                if submitted:
                    with st.spinner("구글 캘린더 정보 가져오는중...", show_time=False):
                        google_events = google_calendar.get_calendar_events()
                    with st.spinner("KTds 캘린더 정보 가져오는중...", show_time=False):
                        try:
                            ktds_events = ktds_calendar.get_calendar_events(ktds_username, ktds_password)
                        except Exception:
                            st.error("사내 메일 주소 또는 비밀번호가 잘못되었습니다. 다시 시도해 주세요.")
                            st.stop()
                    full_events = (google_events or []) + (ktds_events or [])
                    all_events = sorted(full_events, key=lambda e: formatter.extract_start_time(formatter.normalize_korean_ampm(e)))
                    st.session_state["calendar_fetched"] = True
                    st.session_state["calendar_data"] = all_events
                    st.rerun()
                else:
                    st.sidebar.info("KTds 메일 계정 로그인을 완료해 주세요.")
                    all_events = []
            else:
                all_events = st.session_state.get("calendar_data", [])
                st.sidebar.success("KTds 캘린더 연동이 완료되었습니다.")
                if st.sidebar.button("캘린더 다시 불러오기"):
                    st.session_state["calendar_fetched"] = False
                    st.rerun()
        else:
            if not st.session_state["calendar_fetched"]:
                with st.spinner("구글 캘린더 정보 가져오는중...", show_time=True):
                    google_events = google_calendar.get_calendar_events()
                all_events = sorted((google_events or []), key=lambda e: formatter.extract_start_time(formatter.normalize_korean_ampm(e)))
                st.session_state["calendar_fetched"] = True
                st.session_state["calendar_data"] = all_events
            else:
                all_events = st.session_state.get("calendar_data", [])

        # --- Render events ---
        if st.session_state["calendar_fetched"]:
            if all_events:
                indexed_events = [f"{idx}. {e}" for idx, e in enumerate(all_events, start=1)]
                all_events_md = "📅 **일정**\n\n" + "\n\n".join(indexed_events)
                st.info(all_events_md)
                formatted_events = "\n".join(all_events)
            else:
                st.info("오늘은 예정되어 있는 일정이 없습니다.")
                formatted_events = "오늘은 예정되어 있는 일정이 없습니다."

            if st.session_state["calendar_fetched"]:
                if st.button("모닝 브리핑 생성", type="secondary"):
                    output_container = st.container()
                    with output_container:
                        with st.status("모닝 브리핑 생성중...", expanded=True) as status:
                            briefing = azure_agent.retrieve_morning_briefing(formatted_events, lat, lon)
                            if briefing:
                                status.update(label="브리핑 생성 완료!", state="complete")
                                st.markdown(briefing)
                            else:
                                status.update(label="브리핑 생성 실패...", state="error")
                                st.error(f"브리핑 생성에 실패 하였습니다.")
