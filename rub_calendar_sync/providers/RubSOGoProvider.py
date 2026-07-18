from caldav import DAVClient, Calendar, Event

class RubSOGoProvider():
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password
        self.client = DAVClient(
            url=f"https://mail.ruhr-uni-bochum.de/SOGo/dav/{username}",
            username=username,
            password=password,
        )
        self.principal = self.client.principal()

    def get_calendars(self):
        return self.principal.calendars()

    def get_events(self):
        return self._calendar.events()
    
    def set_calendar(self, calendar):
        self._calendar = calendar
    
    @property
    def calendar(self):
        return self._calendar