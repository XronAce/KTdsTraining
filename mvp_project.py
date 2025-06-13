import os

from dotenv import load_dotenv
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential
import streamlit as st
import logging
from authlib.integrations.requests_client import OAuth2Session
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import requests
import statistics

# Load from environment variables
load_dotenv()
endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
agent_id = os.getenv("AGENT_ID")

# --- Configure logging ---
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')

# --- OAuth2 Configuration ---
GOOGLE_CLIENT_ID = st.secrets.auth.client_id
GOOGLE_CLIENT_SECRET = st.secrets.auth.client_secret
GOOGLE_REDIRECT_URI = st.secrets.auth.redirect_uri
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
SCOPES = [
    "openid", "email", "profile",
    "https://www.googleapis.com/auth/calendar.readonly"
]


# Functions
def get_authorization_url():
    client = OAuth2Session(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, scope=SCOPES, redirect_uri=GOOGLE_REDIRECT_URI)
    uri, state = client.create_authorization_url(GOOGLE_AUTHORIZATION_ENDPOINT, access_type='offline', prompt='consent')
    st.session_state['oauth_state'] = state
    return uri


def exchange_token():
    logging.info("Exchanging token...")

    code = st.query_params.get("code")
    if not code:
        st.warning("No code found in query parameters.")
        return

    try:
        client = OAuth2Session(
            GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, scope=SCOPES, redirect_uri=GOOGLE_REDIRECT_URI
        )
        token = client.fetch_token(
            GOOGLE_TOKEN_ENDPOINT,
            code=code
        )
        logging.info("Token successfully fetched")
        st.session_state["google_token"] = token
        st.rerun()
    except Exception as e:
        logging.error(f"Token exchange failed: {e}")
        st.error(f"Token exchange failed: {e}")


def get_calendar_events(max_results: int = 10) -> list[dict] | None:
    try:
        token = st.session_state.get("google_token")
        if not token:
            st.error("No token found in session.")
            return None

        creds = Credentials(
            token=token["access_token"],
            refresh_token=token.get("refresh_token"),
            token_uri=GOOGLE_TOKEN_ENDPOINT,
            client_id=GOOGLE_CLIENT_ID,
            client_secret=GOOGLE_CLIENT_SECRET,
            scopes=SCOPES
        )

        service = build("calendar", "v3", credentials=creds)

        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)

        time_min = today.isoformat() + "Z"
        time_max = tomorrow.isoformat() + "Z"

        events_result = service.events().list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        retrieved_events = events_result.get("items", [])
        if not retrieved_events:
            st.info("There are no upcoming events today.")
            return None

        for event in retrieved_events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            summary = event.get("summary", "No Title")
            st.markdown(f"📅 **{start}** — {summary}")
        return retrieved_events

    except HttpError as error:
        st.error(f"Calendar API error: {error}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None


def format_events(events: list[dict]) -> str:
    formatted = []
    if events:
        for e in events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            summary = e.get("summary", "No Title")
            formatted.append(f"- {start} : {summary}")
    return "\n".join(formatted)


def get_weather_forecast(latitude: float, longitude: float):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        f"&hourly=temperature_2m,weathercode,precipitation"
        f"&timezone=Asia/Seoul"
    )

    response = requests.get(url)
    return response.json()

def get_today_temperature_summary(data):
    today_str = datetime.now().strftime('%Y-%m-%d')
    times = data['hourly']['time']
    temps = data['hourly']['temperature_2m']
    codes = data['hourly']['weathercode']
    precs = data['hourly']['precipitation']

    today_temps = []
    today_codes = []
    today_precs = []

    for t, temp, code, prec in zip(times, temps, codes, precs):
        if t.startswith(today_str):
            today_temps.append(temp)
            today_codes.append(code)
            today_precs.append(prec)

    if not today_temps:
        return {"error": "No data available for today."}

    # Map weather codes to descriptions
    weather_code_description = {
        0: "맑음 ☀️",
        1: "대체로 맑음 🌤️",
        2: "부분적으로 흐림 ⛅",
        3: "흐림 ☁️",
        45: "안개 🌫️",
        48: "서리/안개 🌫️",
        51: "약한 이슬비 🌦️",
        53: "이슬비 🌦️",
        55: "강한 이슬비 🌧️",
        61: "약한 비 🌦️",
        63: "비 🌧️",
        65: "강한 비 🌧️",
        80: "소나기 🌦️",
        81: "소나기 🌧️",
        82: "강한 소나기 🌧️",
    }

    # Pick the most common weather code for the day
    try:
        most_common_code = statistics.mode(today_codes)
    except statistics.StatisticsError:
        most_common_code = today_codes[0] if today_codes else None

    weather_desc = weather_code_description.get(most_common_code, "날씨 정보 없음")

    avg_precip = round(statistics.mean(today_precs), 1)
    precip_msg = ""
    if avg_precip > 0:
        precip_msg = f"오늘 강수량 평균은 {avg_precip}mm로, 비가 올 수 있으니 우산을 챙기세요. ☔"
    else:
        precip_msg = "비 소식은 없습니다. 😊"

    return {
        "date": today_str,
        "temperature_min": min(today_temps),
        "temperature_max": max(today_temps),
        "average_temperature": round(statistics.mean(today_temps), 1),
        "summary": f"{weather_desc} {precip_msg}"
    }


def retrieve_morning_briefing(user_events: str) -> str | None:
    # Add weather forecast data at prompt, fetched from Open-Meteo API
    with st.spinner("Fetching weather forecast..."):
        current_weather_forecast = get_today_temperature_summary(get_weather_forecast(37.5665, 126.9780))

    prompt = f"""
    제가 살고있는 곳의 날씨 정보는 다음과 같습니다:
    {current_weather_forecast}
    
    오늘의 일정은 다음과 같습니다:
    {user_events}
    
    이 정보들을 참고하여, 자연스럽고 친근한 톤의 모닝 브리핑을 작성해 주세요.
    """

    # Instantiate client
    client = AgentsClient(endpoint=endpoint, credential=DefaultAzureCredential())

    # Step 1: Start a new thread
    thread = client.threads.create()

    # Step 2: Send a user message
    user_msg = client.messages.create(
        thread_id=thread.id,
        role="user",
        content=prompt
    )

    # Step 3: Invoke the agent with a run
    with st.spinner("Generating morning briefing...", show_time=True):
        run = client.runs.create_and_process(thread_id=thread.id, agent_id=agent_id)

    if run.status == "completed":
        messages = client.messages.list(thread_id=thread.id)
        for msg in messages:
            if msg.role == "assistant":
                return msg.content[0]['text']['value']
    else:
        st.error("Error occurred while generating morning briefing.")
        print(f"{run.last_error}")
        return None


# --- Streamlit Setup ---
st.set_page_config(page_title="AI Morning Briefing", layout="wide")
st.title("☀️ AI Morning Briefing")

if "google_token" not in st.session_state:
    if st.query_params.get("code"):
        exchange_token()
    else:
        auth_url = get_authorization_url()
        st.markdown(f'<a href="{auth_url}" target="_self"><button>Login with Google</button></a>', unsafe_allow_html=True)
else:
    st.success("Logged in with Google ✅")
    st.button("Log out", on_click=lambda: st.logout())
    events = get_calendar_events()

    if events:
        for event in events:
            logging.info(f"Event: {event}")

    formatted_events = format_events(events)
    if not formatted_events.strip():
        formatted_events = "오늘은 예정되어 있는 일정이 없습니다."

    if st.button("AI Morning Briefing"):
        output_container = st.container()
        with output_container:
            with st.status("Wait a moment...", expanded=True) as status:
                briefing = retrieve_morning_briefing(formatted_events)
                if briefing:
                    status.update(label="Completed!", state="complete")
                    st.markdown(briefing)
                else:
                    status.update(label="Failed to generate briefing.", state="error")
