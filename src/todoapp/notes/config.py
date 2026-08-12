from pydantic_settings import BaseSettings


class NotesConfig(BaseSettings):
    db_path: str = "./notes.db"

    model_config = {"env_prefix": "TODOAPP_NOTES_"}
