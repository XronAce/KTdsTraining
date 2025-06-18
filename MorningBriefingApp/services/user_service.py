import streamlit as st

from auth import google_auth
from database.session import SessionLocal
from models import User, CalendarIntegration


def upsert_user_from_google_profile():
    user_profile = google_auth.fetch_google_userinfo()

    email = user_profile['email']
    name = user_profile['name']

    with SessionLocal() as db:
        existing_user = db.query(User).filter_by(email=email).first()

        if existing_user:
            existing_user.email = email
            existing_user.name = name
        else:
            new_user = User(
                email=email,
                name=name
            )
            db.add(new_user)

        db.commit()


def load_user_data_on_session():
    if "google_profile" not in st.session_state:
        google_auth.fetch_google_userinfo()

    if "user_data" not in st.session_state:
        with SessionLocal() as db:
            existing_user = db.query(User).filter_by(email=st.session_state["google_profile"]['email']).first()
            if existing_user:
                st.session_state["user_data"] = {
                    "user_id": existing_user.user_id,
                    "name": existing_user.name,
                    "email": existing_user.email
                }


def load_user_calendar_integrations_on_session():
    if "calendar_integrations" not in st.session_state:
        with SessionLocal() as db:
            all_cal_integrations = db.query(CalendarIntegration).filter_by(user_id=st.session_state["user_data"]["user_id"]).all()
            st.session_state["calendar_integrations"] = {}
            for cal_integration in all_cal_integrations:
                st.session_state["calendar_integrations"][cal_integration.provider] = {
                    "username": cal_integration.username,
                    "password": cal_integration.password,
                    "access_token": cal_integration.access_token
                }