import os
from datetime import datetime, timedelta

import streamlit as st
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import utils.formatter as formatter

# --- OAuth2 Configuration ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
GOOGLE_AUTHORIZATION_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_ENDPOINT = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_ENDPOINT = "https://openidconnect.googleapis.com/v1/userinfo"
SCOPES = [
    "openid", "email", "profile",
    "https://www.googleapis.com/auth/calendar.readonly"
]


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
            st.info("오늘은 예정되어 있는 일정이 없습니다.")
            return None

        event_lines = []
        for idx, e in enumerate(retrieved_events, start=1):
            start = e["start"].get("dateTime", e["start"].get("date"))
            end = e["end"].get("dateTime", e["end"].get("date"))
            summary = e.get("summary", "No Title")
            start_formatted = formatter.format_time_korean(start)
            end_formatted = formatter.format_time_korean(end)

            if start_formatted == "종일" or end_formatted == "종일":
                time_range = "종일"
            else:
                time_range = f"{start_formatted} ~ {end_formatted}"

            event_lines.append(f"{idx}. {time_range}: {summary}")

        all_events_md = "📅 **일정**\n\n" + "\n\n".join(event_lines)
        st.info(all_events_md)
        return retrieved_events
    except HttpError as error:
        st.error(f"Calendar API error: {error}")
        return None
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None