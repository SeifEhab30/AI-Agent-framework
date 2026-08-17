import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.providers.container import Providers
from todoapp.reminders.config import RemindersConfig
from todoapp.reminders.repo import ReminderRepo
from todoapp.reminders.service import ReminderService


@dataclass
class Runtime:
    app: FastAPI
    service: ReminderService
    providers: Providers


def build_runtime() -> Runtime:
    config = RemindersConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = ReminderRepo(conn)
    service = ReminderService(repo)
    app = FastAPI(title="Reminders")
    return Runtime(app=app, service=service, providers=providers)
