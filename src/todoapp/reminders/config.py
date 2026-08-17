from pydantic_settings import BaseSettings


class RemindersConfig(BaseSettings):
    db_path: str = "./reminders.db"

    model_config = {"env_prefix": "TODOAPP_REMINDERS_"}
