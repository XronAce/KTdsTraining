from datetime import datetime


def format_time_korean(dt_str: str) -> str:
    if "T" not in dt_str:
        return "종일"
    time_part = dt_str.split("T")[1][:5]  # Get "HH:MM"
    hour = int(time_part[:2])
    minute = time_part[3:]

    am_pm = "오전" if hour < 12 else "오후"
    hour_12 = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)

    return f"{am_pm} {hour_12}:{minute}"


def extract_start_time(event_str: str) -> datetime:
    time_part = event_str.split(" - ")[0]
    return datetime.strptime(time_part.strip(), "%p %I:%M")


def normalize_korean_ampm(event_str: str) -> str:
    return event_str.replace("오전", "AM").replace("오후", "PM")