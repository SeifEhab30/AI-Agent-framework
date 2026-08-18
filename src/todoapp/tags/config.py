from pydantic_settings import BaseSettings


class TagsConfig(BaseSettings):
    db_path: str = "./tags.db"

    model_config = {"env_prefix": "TODOAPP_TAGS_"}
