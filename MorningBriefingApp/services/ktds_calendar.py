import logging
import os
import zoneinfo
from datetime import datetime, timedelta
from urllib.parse import unquote

from caldav import DAVClient
from caldav.collection import Principal

import utils.formatter as formatter

# Enable debug logging
logging.basicConfig(level=logging.WARN, format='%(asctime)s - %(levelname)s - %(message)s')


def get_calendar_events() -> list | None:
    username = os.getenv("KTDS_USERNAME")
    url = f"https://groupmail.kt.co.kr:1985/dav/users/{username}/"
    password = os.getenv("KTDS_PASSWORD")

    # Connect to server
    client = DAVClient(url, username=username, password=password)

    # Attempt to discover calendars
    principal = Principal(client=client, url=url)
    calendars = principal.calendars()

    # Print calendars found
    personal_ktds_calendar = None
    for i, cal in enumerate(calendars):
        if unquote(str(cal.url)) == f"https://groupmail.kt.co.kr:1985/dav/{username}/calendar/":
            print(f"found calendar via url: {cal.url}")
            personal_ktds_calendar = cal

    calendar = personal_ktds_calendar if personal_ktds_calendar else calendars[0]

    # Fetch today's events
    today = datetime.now(tz=zoneinfo.ZoneInfo("Asia/Seoul")).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    events = calendar.search(
        start=today,
        end=tomorrow,
        event=True,
        expand=False,
    )

    event_lines = []
    for event in events:
        try:
            vevent = event.vobject_instance.vevent
            summary = vevent.summary.value
            start = formatter.format_time_korean(str(vevent.dtstart.value).replace(" ", "T"))
            end = formatter.format_time_korean(str(vevent.dtend.value).replace(" ", "T"))
            if start == "종일" or end == "종일":
                time_range = "종일"
            else:
                time_range = f"{start} - {end}"

            event_lines.append(f"{time_range}: [KTds] {summary}")
        except Exception as e:
            print(f"[Skipped event due to error] {e}")

    return event_lines