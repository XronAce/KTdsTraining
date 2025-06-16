import statistics
from datetime import datetime

import requests


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