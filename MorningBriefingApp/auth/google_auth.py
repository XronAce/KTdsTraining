import logging
import os

import requests
import streamlit as st
from authlib.integrations.requests_client import OAuth2Session

from services.user_service import upsert_user_from_google_profile, load_user_data_on_session, load_user_calendar_integrations_on_session

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

# --- Configure logging ---
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')


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
        upsert_user_from_google_profile()
        load_user_data_on_session()
        load_user_calendar_integrations_on_session()
        st.rerun()
    except Exception as e:
        logging.error(f"Token exchange failed: {e}")
        st.error(f"Token exchange failed: {e}")


def fetch_google_userinfo() -> dict | None:
    token = st.session_state.get("google_token")
    if not token:
        st.warning("No token found.")
        return None
    access_token = token["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    resp = requests.get("https://openidconnect.googleapis.com/v1/userinfo", headers=headers)
    if resp.status_code == 200:
        if "google_profile" not in st.session_state:
            st.session_state["google_profile"] = resp.json()
        return resp.json()
    else:
        st.error("Failed to fetch user info.")
        return None