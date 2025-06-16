import streamlit as st


def google_login_button(auth_url: str):
    return st.markdown(f"""
            <a href="{auth_url}" target="_self" style="
                display: inline-block;
                padding: 0.5rem 1rem;
                background-color: #4285F4;
                color: white;
                border: none;
                border-radius: 4px;
                text-decoration: none;
                font-size: 14px;
                font-weight: 500;
                font-family: 'Segoe UI', sans-serif;
            ">
                Google 로그인
            </a>
            """, unsafe_allow_html=True)
