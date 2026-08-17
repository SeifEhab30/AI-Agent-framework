import sqlite3
from dataclasses import dataclass

from fastapi import FastAPI

from todoapp.providers.container import Providers
from todoapp.todos.config import TodosConfig
from todoapp.todos.repo import TodoRepo
from todoapp.todos.service import TodoService


@dataclass
class Runtime:
    app: FastAPI
    service: TodoService
    providers: Providers


def build_runtime() -> Runtime:
    config = TodosConfig()
    providers = Providers.build()
    conn = sqlite3.connect(config.db_path, check_same_thread=False)
    repo = TodoRepo(conn)
    service = TodoService(repo)
    app = FastAPI(title="Todos")
    return Runtime(app=app, service=service, providers=providers)
