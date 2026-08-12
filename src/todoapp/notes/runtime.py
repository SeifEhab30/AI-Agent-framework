import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.notes.config import NotesConfig
from todoapp.notes.repo import NoteRepo
from todoapp.notes.service import NoteService
from todoapp.providers.container import Providers


@dataclass
class Runtime:
    app: FastAPI
    service: NoteService
    providers: Providers


def build_runtime() -> Runtime:
    config = NotesConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = NoteRepo(conn)
    service = NoteService(repo)
    app = FastAPI(title="Notes")
    return Runtime(app=app, service=service, providers=providers)
