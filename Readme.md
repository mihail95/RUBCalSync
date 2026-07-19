# RUBCalSync

A Python utility for synchronizing events between multiple calendar providers using a common event model.

Current providers:
- RUB SOGo (CalDAV)
> **Note:** Only the RUB SOGo calendar (`https://mail.ruhr-uni-bochum.de/SOGo`) is supported. The simplified `rubwebmail` calendar is not accessible via CalDAV.
<!-- - Google Calendar -->



## Installation

1. Clone the repository.
2. *(Optional)* Create a virtual environment: ``python3 -m venv .venv``
3. Install the project in editable mode: ``pip install -e .``
4. Create a `settings.json` file (see **Configuration**).
5. Run the synchronizer: ``rubcalsync``

## Configuration

Before running the synchronizer, create a `settings.json` file from the provided `template-settings.json` file by copying or renaming it.

The file should contain the credentials required for the configured source and target providers.

Currently implemented:
- RUB LoginID
- RUB password
<!-- TODO: - Google Calendar configuration -->
<!-- TODO: - Google OAuth credentials -->

## Command Line Arguments

The synchronizer can be run interactively or non-interactively. ``rubcalsync [OPTIONS]``

Available options:

| Option              | Description                                                |
| ------------------- | ---------------------------------------------------------- |
| `--source-provider` | Source calendar provider                                   |
| `--target-provider` | Target calendar provider                                   |
| `--source-calendar` | Name of the source calendar                                |
| `--target-calendar` | Name of the target calendar                                |
| `--dry-run`         | Show planned changes without modifying the target calendar |


Example: 
```
rubcalsync \
    --source-provider RubSOGo \
    --source-calendar "Persönlicher Kalender" \
    --target-provider Google \
    --target-calendar "Personal" \
    --dry-run
```

## Automation

The synchronizer can be automated using tools such as:

- `systemd` timers (Linux)
- `cron` (Linux/macOS)
- Windows Task Scheduler

When all providers and calendars are specified via command-line arguments, the synchronizer can run unattended without user interaction.

## Roadmap
- [x] Read events from RUB SOGo (CalDAV)
- [x] Create, update and delete events in RUB SOGo - TODO: need to test those
- [ ] Google Calendar integration
- [ ] Event synchronization
- [ ] Scheduled synchronization
- [ ] Support for additional CalDAV providers