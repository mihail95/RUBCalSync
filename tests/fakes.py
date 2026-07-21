from copy import deepcopy
from typing import Any

from rub_calendar_sync.models import Event
from rub_calendar_sync.providers import BaseCalendarProvider


class FakeCalendar:
    def __init__(self, name: str = "Fake Calendar") -> None:
        self.name = name

    def get_display_name(self) -> str:
        return self.name


class FakeCalendarProvider(BaseCalendarProvider):
    can_read = True
    can_write = True

    def __init__(self, events: list[Event] | None = None, calendar_name: str = "Fake Calendar") -> None:
        self._calendar = FakeCalendar(calendar_name)
        self._events = {
            event.uid: deepcopy(event)
            for event in events or []
        }

        self.created: list[Event] = []
        self.updated: list[Event] = []
        self.deleted: list[str] = []

    @property
    def calendar(self) -> FakeCalendar:
        return self._calendar

    def get_calendars(self) -> list[FakeCalendar]:
        return [self._calendar]

    def set_calendar(self, calendar: FakeCalendar) -> None:
        self._calendar = calendar

    def get_events(self, refresh: bool = False) -> list[Event]:
        return list(self._events.values())

    def create_event(self, event: Event) -> None:
        copied = deepcopy(event)
        self._events[event.uid] = copied
        self.created.append(copied)

    def update_event(self, event: Event) -> None:
        if event.uid not in self._events:
            raise ValueError(f"Event with UID {event.uid} not found.")

        copied = deepcopy(event)
        self._events[event.uid] = copied
        self.updated.append(copied)

    def delete_event(self, uid: str) -> None:
        if uid not in self._events:
            raise ValueError(f"Event with UID {uid} not found.")

        del self._events[uid]
        self.deleted.append(uid)