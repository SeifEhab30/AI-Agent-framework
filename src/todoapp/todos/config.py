from pydantic_settings import BaseSettings


class TodosConfig(BaseSettings):
    db_path: str = "./todos.db"

    model_config = {"env_prefix": "TODOAPP_TODOS_"}
