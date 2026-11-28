from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "SprintFlow"
    DATABASE_URL: str = "postgresql+psycopg://sprintflow:sprintflow_password@localhost:5432/sprintflow"

    # JWT Authentication Settings
    JWT_SECRET_KEY: str = "sprintflow-dev-insecure-secret-key-at-least-32-chars-long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI Integration Settings
    GEMINI_API_KEY: str | None = None

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
