import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.bookmarks.config import BookmarksConfig
from todoapp.bookmarks.repo import BookmarkRepo
from todoapp.bookmarks.service import BookmarkService
from todoapp.providers.container import Providers


@dataclass
class Runtime:
    app: FastAPI
    service: BookmarkService
    providers: Providers


def build_runtime() -> Runtime:
    config = BookmarksConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = BookmarkRepo(conn)
    service = BookmarkService(repo)
    app = FastAPI(title="Bookmarks")
    return Runtime(app=app, service=service, providers=providers)
