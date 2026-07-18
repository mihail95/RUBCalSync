import argparse
import json
from pathlib import Path
from typing import Any

from rich import box
from rich.console import Console
from rich.prompt import IntPrompt
from rich.table import Table

from rub_calendar_sync.providers import (
    BaseCalendarProvider,
    GoogleProvider,
    RubSOGoProvider,
)


console = Console()

PROVIDERS: dict[str, type[BaseCalendarProvider]] = {
    "RubSOGo": RubSOGoProvider,
    "Google": GoogleProvider,
}

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTINGS_FILE = PROJECT_ROOT / "settings.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synchronize calendars between configured providers.")

    parser.add_argument("--source-provider", help="Name of the source provider configured in settings.json.")
    parser.add_argument("--target-provider", help="Name of the target provider configured in settings.json.")
    parser.add_argument("--source-calendar", help="Name of the source calendar to synchronize.")
    parser.add_argument("--target-calendar", help="Name of the target calendar.")
    parser.add_argument("--dry-run", action="store_true", help="Show intended changes without modifying the target calendar.")

    return parser.parse_args()


def load_settings(filepath: Path) -> dict[str, Any]:
    try:
        with filepath.open("r", encoding="utf-8") as file:
            settings = json.load(file)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Settings file not found: {filepath}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(
            f"Invalid JSON in settings file at "
            f"line {exc.lineno}, column {exc.colno}: {exc.msg}"
        ) from exc
    except OSError as exc:
        raise RuntimeError(f"Could not read settings file: {exc}") from exc

    if not isinstance(settings, dict):
        raise RuntimeError("The settings file must contain a JSON object.")

    return settings


def new_step(title: str) -> None:
    console.clear()
    console.rule(f"[bold white]{title}[/bold white]")


def show_startup() -> None:
    console.clear()
    console.rule("[bold white]RUBCalSync[/bold white]")
    console.print("Synchronize events between configured calendar providers.\n", style="white")


def info(message: str) -> None:
    console.print(f"[cyan]{message}[/cyan]")


def success(message: str) -> None:
    console.print(f"[green]✓ {message}[/green]")


def error(message: str) -> None:
    console.print(f"[red]✗ {message}[/red]")


def get_calendar_name(calendar: Any) -> str:
    if hasattr(calendar, "get_display_name"):
        return str(calendar.get_display_name())

    if hasattr(calendar, "name"):
        return str(calendar.name)

    return str(calendar)


def get_available_provider_names(settings: dict[str, Any]) -> list[str]:
    return [ name for name in settings if name in PROVIDERS ]


def choose_provider(settings: dict[str, Any], title: str) -> str:
    provider_names = get_available_provider_names(settings)

    if not provider_names:
        raise RuntimeError("No supported providers were found in settings.json.")

    new_step(title)

    table = Table(box=box.MINIMAL)
    table.add_column("#", justify="right")
    table.add_column("Provider")

    for index, provider_name in enumerate(provider_names, start=1):
        table.add_row(str(index), provider_name)

    console.print("[bold cyan]Available providers[/bold cyan]\n")
    console.print(table)

    choice = IntPrompt.ask(
        "Select a provider",
        choices=[ str(index) for index in range(1, len(provider_names) + 1) ],
        default=1,
    )

    return provider_names[choice - 1]


def create_provider(name: str, settings: dict[str, Any]) -> BaseCalendarProvider:
    if name not in PROVIDERS:
        raise ValueError(f"Unsupported provider: {name}")

    if name not in settings:
        raise ValueError(
            f"No configuration for provider '{name}' "
            "was found in settings.json."
        )

    provider_class = PROVIDERS[name]
    provider_settings = settings[name]

    if not isinstance(provider_settings, dict):
        raise ValueError(
            f"The configuration for '{name}' must be a JSON object."
        )

    return provider_class(**provider_settings)


def find_calendar(provider: BaseCalendarProvider, calendar_name: str) -> Any:
    calendars = provider.get_calendars()

    for calendar in calendars:
        if get_calendar_name(calendar) == calendar_name:
            return calendar

    raise ValueError(f"Calendar '{calendar_name}' was not found.")


def prompt_for_calendar(provider: BaseCalendarProvider, title: str) -> Any:
    new_step(title)

    calendars = list(provider.get_calendars())

    if not calendars:
        raise RuntimeError("The selected provider has no calendars.")

    console.print("[bold cyan]Available calendars[/bold cyan]\n")
    table = Table(box=box.MINIMAL)
    table.add_column("#", justify="right")
    table.add_column("Calendar")

    for index, calendar in enumerate(calendars, start=1):
        table.add_row(str(index), get_calendar_name(calendar))

    console.print(table)

    choice = IntPrompt.ask(
        "Select a calendar",
        choices=[str(index) for index in range(1, len(calendars) + 1)],
        default=1,
    )

    return calendars[choice - 1]


def select_calendar(provider: BaseCalendarProvider, calendar_name: str | None, title: str) -> Any:
    if calendar_name:
        return find_calendar(provider, calendar_name)

    return prompt_for_calendar(provider, title)


def show_summary(source_provider_name: str, source_provider: BaseCalendarProvider, target_provider_name: str, target_provider: BaseCalendarProvider, dry_run: bool) -> None:
    new_step("Synchronization Summary")

    console.print("[bold cyan]Synchronization Summary[/bold cyan]\n")
    table = Table(show_header=False, box=box.MINIMAL)
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("Source provider", source_provider_name)
    table.add_row("Source calendar", get_calendar_name(source_provider.calendar))
    table.add_row("Target provider", target_provider_name)
    table.add_row("Target calendar", get_calendar_name(target_provider.calendar))
    table.add_row("Mode", "Dry run" if dry_run else "Synchronization")

    console.print(table)
    console.print()


def sync(source: BaseCalendarProvider, target: BaseCalendarProvider, dry_run: bool = False) -> None:
    source_events = list(source.get_events())

    info(
        f"Found {len(source_events)} event(s) in "
        f"'{get_calendar_name(source.calendar)}'."
    )

    for event in source_events:
        # Replace this with the actual comparison and synchronization logic.
        if dry_run:
            console.print(
                "[yellow]Would process:[/yellow] "
                f"{event.data}"
            )
        else:
            console.print(
                "[cyan]Processing:[/cyan] "
                f"{event.data}"
            )

    if dry_run:
        success("Dry run completed. No changes were made.")
    else:
        success("Synchronization completed.")


def main() -> None:
    args = parse_args()
    show_startup()

    try:
        settings = load_settings(SETTINGS_FILE)

        source_provider_name = (
            args.source_provider
            or choose_provider(
                settings,
                "Choose Source Provider",
            )
        )

        new_step("Connecting to Source Provider")
        info(f"Connecting to {source_provider_name}...")
        source_provider = create_provider(source_provider_name, settings)
        success(f"Connected to {source_provider_name}.")

        source_calendar = select_calendar(source_provider, args.source_calendar, "Choose Source Calendar")
        source_provider.set_calendar(source_calendar)

        target_provider_name = (
            args.target_provider
            or choose_provider(
                settings,
                "Choose Target Provider",
            )
        )

        new_step("Connecting to Target Provider")
        info(f"Connecting to {target_provider_name}...")
        target_provider = create_provider(target_provider_name, settings)
        success(f"Connected to {target_provider_name}.")

        target_calendar = select_calendar(target_provider, args.target_calendar, "Choose Target Calendar")
        target_provider.set_calendar(target_calendar)

        show_summary(
            source_provider_name=source_provider_name,
            source_provider=source_provider,
            target_provider_name=target_provider_name,
            target_provider=target_provider,
            dry_run=args.dry_run,
        )

        sync(source=source_provider, target=target_provider, dry_run=args.dry_run)

    except (RuntimeError, ValueError, TypeError) as exc:
        error(str(exc))
        raise SystemExit(1) from exc
    except KeyboardInterrupt:
        console.print()
        error("Synchronization cancelled.")
        raise SystemExit(130)


if __name__ == "__main__":
    main()