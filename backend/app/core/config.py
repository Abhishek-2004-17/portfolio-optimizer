from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    PROJECT_NAME: str = "Finance Portfolio Optimizer"
    API_V1_PREFIX: str = "/api"
    DATABASE_URL: str = "postgresql+psycopg2://portfolio:portfolio@localhost:5432/portfolio_db"
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    RISK_FREE_RATE: float = 0.04
    DEFAULT_TRADING_DAYS: int = 252


settings = Settings()
