from typing import Any

from caldav import DAVClient
from rub_calendar_sync.models import Event


class RubSOGoProvider:
    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password

        self.client = DAVClient(
            url=f"https://mail.ruhr-uni-bochum.de/SOGo/dav/{username}/",
            username=username,
            password=password,
        )

        self.principal = self.client.principal()
        self._calendar: Any | None = None
        self._events: list[Event] | None = None

    def get_calendars(self):
        return self.principal.calendars()

    def set_calendar(self, calendar) -> None:
        self._calendar = calendar
        self._events = None

    @property
    def calendar(self):
        if self._calendar is None:
            raise RuntimeError("No calendar has been selected.")

        return self._calendar

    def _convert_event(self, caldav_event) -> Event:
        ical = caldav_event.get_icalendar_component()

        return Event(
            uid=str(ical["UID"]),
            summary=str(ical.get("SUMMARY", "")),
            start=ical["DTSTART"].dt,
            end=ical["DTEND"].dt,
            description=str(ical.get("DESCRIPTION", "")) or None,
            location=str(ical.get("LOCATION", "")) or None,
        )

    def get_events(self, refresh: bool = False) -> list[Event]:
        if refresh or self._events is None:
            self._events = [
                self._convert_event(event)
                for event in self.calendar.events()
            ]

        return self._events