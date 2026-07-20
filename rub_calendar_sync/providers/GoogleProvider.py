from pathlib import Path

from caldav import DAVClient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from rub_calendar_sync.providers import CalDAVProvider


class GoogleProvider(CalDAVProvider):
    can_read = True
    can_write = True

    AUTH_SCOPES = [
        "https://www.googleapis.com/auth/calendar",
    ]

    def __init__(self, token_path: str = "google-token.json", credentials_path: str = "google-oauth-credentials.json",) -> None:
        credentials = self._load_credentials(
            token_path=Path(token_path),
            credentials_path=Path(credentials_path),
        )

        client = DAVClient(
            url="https://apidata.googleusercontent.com/caldav/v2/",
            headers={
                "Authorization": f"Bearer {credentials.token}",
            },
        )

        super().__init__(client)

    def _load_credentials(
        self,
        token_path: Path,
        credentials_path: Path,
    ) -> Credentials:
        if not credentials_path.exists():
            raise FileNotFoundError(
                f"Google OAuth credentials file not found: "
                f"{credentials_path}"
            )

        if not token_path.exists():
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path),
                self.AUTH_SCOPES,
            )

            credentials = flow.run_local_server(port=0)
            token_path.write_text(
                credentials.to_json(),
                encoding="utf-8",
            )

            return credentials

        credentials = Credentials.from_authorized_user_file(
            str(token_path),
            self.AUTH_SCOPES,
        )

        if credentials.expired:
            if not credentials.refresh_token:
                raise RuntimeError(
                    "Google token has expired and no refresh token is "
                    "available. Delete the token file and authenticate again."
                )

            credentials.refresh(Request())
            token_path.write_text(
                credentials.to_json(),
                encoding="utf-8",
            )

        return credentials