from pydantic_settings import BaseSettings


class LabelsConfig(BaseSettings):
    db_path: str = "./labels.db"

    model_config = {"env_prefix": "TODOAPP_LABELS_"}
