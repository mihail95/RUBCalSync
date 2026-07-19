from typing import Any

from caldav import DAVClient
from rub_calendar_sync.providers import BaseCalendarProvider
from rub_calendar_sync.models import Event


class RubSOGoProvider(BaseCalendarProvider):
    can_read = True
    can_write = True

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
            rrule=ical.get("RRULE", None)
        )

    def get_events(self, refresh: bool = False) -> list[Event]:
        if refresh or self._events is None:
            self._events = [
                self._convert_event(event)
                for event in self.calendar.events()
            ]

        return self._events
    
    def create_event(self, event: Event) -> None:
        self.calendar.add_event(
            uid=event.uid,
            dtstart=event.start,
            dtend=event.end,
            summary=event.summary,
            description=event.description,
            location=event.location,
            rrule=event.rrule,
        )
        self._events = None
    
    def update_event(self, event: Event) -> None:
        caldav_event = self.calendar.get_event_by_uid(event.uid)

        with caldav_event.edit_icalendar_component() as ical:
            ical["SUMMARY"] = event.summary

            ical.pop("DTSTART", None)
            ical.add("DTSTART", event.start)

            ical.pop("DTEND", None)
            ical.add("DTEND", event.end)

            ical.pop("DESCRIPTION", None)
            if event.description is not None:
                ical.add("DESCRIPTION", event.description)

            ical.pop("LOCATION", None)
            if event.location is not None:
                ical.add("LOCATION", event.location)

            ical.pop("RRULE", None)
            if event.rrule is not None:
                ical.add("RRULE", event.rrule)

        caldav_event.save()
        self._events = None

    def delete_event(self, uid: str) -> None:
        for caldav_event in self.calendar.events():
            ical = caldav_event.get_icalendar_component()
            if str(ical["UID"]) == uid:
                caldav_event.delete()
                return

        raise ValueError(f"Event with UID {uid} not found.")