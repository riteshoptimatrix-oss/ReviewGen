from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional

class Settings(BaseSettings):
    debug_extraction: bool = False
    http_timeout_seconds: int = 20
    max_redirects: int = 10

    # MongoDB connection settings
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "business_cache"

    cache_ttl_hours: int = 168
    max_concurrent_requests: int = 10
    retry_attempts: int = 3
    api_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    max_bulk_urls: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
