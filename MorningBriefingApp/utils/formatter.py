def format_time_korean(dt_str: str) -> str:
    if "T" not in dt_str:
        return "종일"
    time_part = dt_str.split("T")[1][:5]  # Get "HH:MM"
    hour = int(time_part[:2])
    minute = time_part[3:]

    am_pm = "오전" if hour < 12 else "오후"
    hour_12 = hour if 1 <= hour <= 12 else (hour - 12 if hour > 12 else 12)

    return f"{am_pm} {hour_12}:{minute}"


def format_events(calendar_events: list[dict]) -> str:
    formatted = []
    if calendar_events:
        for e in calendar_events:
            start = e["start"].get("dateTime", e["start"].get("date"))
            summary = e.get("summary", "No Title")
            formatted.append(f"- {start} : {summary}")
    return "\n".join(formatted)