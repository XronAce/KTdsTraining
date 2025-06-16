import os

import streamlit as st
from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

import services.weather_forecast as weather_forecast

endpoint = os.getenv("AZURE_AI_FOUNDRY_ENDPOINT")
agent_id = os.getenv("AGENT_ID")


def retrieve_morning_briefing(user_events: str, latitude: float, longitude: float) -> str | None:
    # Add weather forecast data at prompt, fetched from Open-Meteo API
    with st.spinner("현재 날씨 정보 조회중..."):
        current_weather_forecast = weather_forecast.get_today_temperature_summary(weather_forecast.get_weather_forecast(latitude, longitude))

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
    with st.spinner("모닝 브리핑 생성중...", show_time=True):
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