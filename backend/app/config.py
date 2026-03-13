from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://vqi:vqi_dev_password@localhost:5432/vqi_georgia"
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    CORS_ORIGINS: str = "http://localhost:3000"
    AUDIT_SAMPLE_RATE: float = 0.10  # 10% random audit

    model_config = {"env_file": ".env"}


settings = Settings()
