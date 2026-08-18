import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.labels.config import LabelsConfig
from todoapp.labels.repo import LabelRepo
from todoapp.labels.service import LabelService
from todoapp.providers.container import Providers


@dataclass
class Runtime:
    app: FastAPI
    service: LabelService
    providers: Providers


def build_runtime() -> Runtime:
    config = LabelsConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = LabelRepo(conn)
    service = LabelService(repo)
    app = FastAPI(title="Labels")
    return Runtime(app=app, service=service, providers=providers)
