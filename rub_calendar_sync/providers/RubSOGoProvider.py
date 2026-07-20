from caldav import DAVClient

from rub_calendar_sync.providers import CalDAVProvider


class RubSOGoProvider(CalDAVProvider):
    can_read = True
    can_write = True
    
    def __init__(self, username: str, password: str) -> None:
        client = DAVClient(
            url=f"https://mail.ruhr-uni-bochum.de/SOGo/dav/{username}/",
            username=username,
            password=password,
        )

        super().__init__(client)