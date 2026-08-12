from pydantic_settings import BaseSettings


class BookmarksConfig(BaseSettings):
    db_path: str = "./bookmarks.db"

    model_config = {"env_prefix": "TODOAPP_BOOKMARKS_"}
