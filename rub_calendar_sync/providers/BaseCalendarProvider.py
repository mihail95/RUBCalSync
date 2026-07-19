from abc import ABC, abstractmethod
from typing import Any

class BaseCalendarProvider(ABC):
    can_read: bool = True
    can_write: bool = False

    @abstractmethod
    def get_events(self):
        ...

    @abstractmethod
    def create_event(self, event):
        ...

    @abstractmethod
    def update_event(self, event):
        ...

    @abstractmethod
    def delete_event(self, uid):
        ...
    
    @abstractmethod
    def get_calendars(self):
        ...
    
    @property
    @abstractmethod
    def calendar(self) -> Any:
        ...