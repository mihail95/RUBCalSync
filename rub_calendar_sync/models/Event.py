from dataclasses import dataclass
from datetime import date, datetime


@dataclass(slots=True)
class Event:
    uid: str
    summary: str
    start: date | datetime
    end: date | datetime
    location: str | None = None
    description: str | None = None