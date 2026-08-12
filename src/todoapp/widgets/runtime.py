import sqlite3

from fastapi import FastAPI

from todoapp.providers.container import Providers
from todoapp.widgets.config import WidgetsConfig
from todoapp.widgets.repo import WidgetRepo
from todoapp.widgets.service import WidgetService


def build_app() -> FastAPI:
    config = WidgetsConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = WidgetRepo(conn)
    service = WidgetService(repo)

    from todoapp.widgets.ui import build_router

    app = FastAPI(title="Widgets")
    app.include_router(build_router(service, providers))
    return app


app = build_app()
