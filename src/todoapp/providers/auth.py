from dataclasses import dataclass


@dataclass(frozen=True)
class CurrentUser:
    id: str
    name: str


class AuthProvider:
    """Stub: always returns a fixed dev user. Replace with real auth later."""

    def current_user(self) -> CurrentUser:
        return CurrentUser(id="dev-user", name="Dev User")
