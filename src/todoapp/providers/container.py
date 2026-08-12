from dataclasses import dataclass

from todoapp.providers.auth import AuthProvider
from todoapp.providers.telemetry import TelemetryProvider


@dataclass
class Providers:
    """Composition root for cross-cutting dependencies. Built once by
    runtime.py and passed into service/repo constructors — no service or
    repo module imports this module directly."""

    auth: AuthProvider
    telemetry: TelemetryProvider

    @classmethod
    def build(cls) -> "Providers":
        return cls(auth=AuthProvider(), telemetry=TelemetryProvider())
