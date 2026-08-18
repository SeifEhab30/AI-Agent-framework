import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.providers.container import Providers
from todoapp.tags.config import TagsConfig
from todoapp.tags.repo import TagRepo
from todoapp.tags.service import TagService


@dataclass
class Runtime:
    app: FastAPI
    service: TagService
    providers: Providers


def build_runtime() -> Runtime:
    config = TagsConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = TagRepo(conn)
    service = TagService(repo)
    app = FastAPI(title="Tags")
    return Runtime(app=app, service=service, providers=providers)
