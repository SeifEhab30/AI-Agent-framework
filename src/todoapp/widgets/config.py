from pydantic_settings import BaseSettings


class WidgetsConfig(BaseSettings):
    db_path: str = "./widgets.db"

    model_config = {"env_prefix": "TODOAPP_WIDGETS_"}
