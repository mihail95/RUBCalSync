# RUBCalSync

A Python utility that synchronizes events from a RUB SOGo calendar to a Google Calendar.

> **Note:** Only the RUB SOGo calendar (`https://mail.ruhr-uni-bochum.de/SOGo`) is currently supported. The legacy `rubwebmail` calendar is not accessible via CalDAV.

## Installation

1. Clone the repository.
2. *(Optional)* Create a virtual environment: ``python3 -m venv .venv``
3. Install the project in editable mode: ``pip install -e .``
4. TODO: settings.json - how to use
5. Run the synchronizer: ``rubcalsync``

## Configuration

Before running the synchronizer, create a `settings.json` file from the provided `template-settings.json` file by renaming or copying it.

- RUB LoginID
- RUB password
- Google Calendar configuration
- Google OAuth credentials

## Automation
Can be automated by either running it on a schedule with ``systemd`` or ``Windows Task Scheduler``