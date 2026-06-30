from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        protected_namespaces=(),
    )

    app_name: str = "PredictiveOps AI"
    api_v1_prefix: str = "/api/v1"
    environment: str = Field(default="development")
    database_url: str = Field(default="sqlite:///./predictiveops.db")
    mlflow_tracking_uri: str = Field(default="file:./mlflow")
    model_dir: str = Field(default="ml/models")
    reports_dir: str = Field(default="ml/reports")
    raw_data_dir: str = Field(default="ml/data/raw")
    processed_data_dir: str = Field(default="ml/data/processed")
    risk_threshold: float = Field(default=0.65)
    # LLM root-cause: leave api_key empty → heuristic-only mode (no external calls)
    # For OpenAI: set ROOT_CAUSE_API_KEY=sk-...
    # For Groq:   set ROOT_CAUSE_API_KEY=gsk_... + OPENAI_BASE_URL=https://api.groq.com/openai/v1
    root_cause_api_key: str | None = Field(default=None)
    root_cause_model: str = Field(default="gpt-4o-mini")
    openai_base_url: str | None = Field(default=None)  # override for Groq / other providers
    allowed_origins: str = Field(default="http://localhost:5173")

    def ensure_dirs(self) -> None:
        for folder in [self.model_dir, self.reports_dir, self.raw_data_dir, self.processed_data_dir]:
            Path(folder).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_dirs()
    return settings
