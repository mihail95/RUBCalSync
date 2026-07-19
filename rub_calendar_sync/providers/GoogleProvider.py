from rub_calendar_sync.providers import BaseCalendarProvider

class GoogleProvider(BaseCalendarProvider):
    can_read = True
    can_write = True
    
    def __init__(self):
        ...

    def get_calendars(self):
        ...

    def get_events():
        ...