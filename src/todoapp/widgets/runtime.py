import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.providers.container import Providers
from todoapp.widgets.config import WidgetsConfig
from todoapp.widgets.repo import WidgetRepo
from todoapp.widgets.service import WidgetService


@dataclass
class Runtime:
    app: FastAPI
    service: WidgetService
    providers: Providers


def build_runtime() -> Runtime:
    config = WidgetsConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = WidgetRepo(conn)
    service = WidgetService(repo)
    app = FastAPI(title="Widgets")
    return Runtime(app=app, service=service, providers=providers)
