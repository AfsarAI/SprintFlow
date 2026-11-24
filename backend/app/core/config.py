from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SprintFlow"
    DATABASE_URL: str = "postgresql+psycopg://sprintflow:sprintflow_password@localhost:5432/sprintflow"

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
