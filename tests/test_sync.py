from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from rub_calendar_sync.models import Event
from rub_calendar_sync.sync_cals import sync

from .fakes import FakeCalendarProvider


BERLIN = ZoneInfo("Europe/Berlin")


def make_event(uid: str = "event-1", summary: str = "Meeting", description: str | None = None, location: str | None = None, rrule: str | None = None) -> Event:
    return Event(
        uid=uid,
        summary=summary,
        start=datetime(2026, 7, 21, 10, 0, tzinfo=BERLIN),
        end=datetime(2026, 7, 21, 11, 0, tzinfo=BERLIN),
        description=description,
        location=location,
        rrule=rrule,
    )


def test_creates_missing_event() -> None:
    event = make_event()

    source = FakeCalendarProvider([event])
    target = FakeCalendarProvider()

    sync(source, target)

    assert target.created == [event]
    assert target.updated == []
    assert target.get_events() == [event]


def test_does_nothing_when_event_is_unchanged() -> None:
    event = make_event()

    source = FakeCalendarProvider([event])
    target = FakeCalendarProvider([event])

    sync(source, target)

    assert target.created == []
    assert target.updated == []


def test_updates_changed_event() -> None:
    source_event = make_event(summary="New title")
    target_event = make_event(summary="Old title")

    source = FakeCalendarProvider([source_event])
    target = FakeCalendarProvider([target_event])

    sync(source, target)

    assert target.created == []
    assert target.updated == [source_event]
    assert target.get_events() == [source_event]


def test_dry_run_does_not_create_event() -> None:
    event = make_event()

    source = FakeCalendarProvider([event])
    target = FakeCalendarProvider()

    sync(source, target, dry_run=True)

    assert target.created == []
    assert target.updated == []
    assert target.get_events() == []


def test_dry_run_does_not_update_event() -> None:
    source_event = make_event(summary="New title")
    target_event = make_event(summary="Old title")

    source = FakeCalendarProvider([source_event])
    target = FakeCalendarProvider([target_event])

    sync(source, target, dry_run=True)

    assert target.created == []
    assert target.updated == []
    assert target.get_events() == [target_event]


def test_rejects_unreadable_source() -> None:
    source = FakeCalendarProvider()
    source.can_read = False

    target = FakeCalendarProvider()

    with pytest.raises(
        ValueError,
        match="cannot be used as a source",
    ):
        sync(source, target)


def test_rejects_unwritable_target() -> None:
    source = FakeCalendarProvider()

    target = FakeCalendarProvider()
    target.can_write = False

    with pytest.raises(
        ValueError,
        match="cannot be used as a target",
    ):
        sync(source, target)