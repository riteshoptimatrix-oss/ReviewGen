from pydantic_settings import BaseSettings, SettingsConfigDict

from typing import Optional

class Settings(BaseSettings):
    debug_extraction: bool = False
    http_timeout_seconds: int = 20
    max_redirects: int = 10

    # MongoDB connection settings
    mongodb_uri: str = "mongodb+srv://riteshoptimatrix_db_user:TSNcuwbtaXPtloTA@reviewdbcluster.a9tkxni.mongodb.net/?appName=reviewdbcluster"
    mongodb_db_name: str = "business_cache"

    # MySQL connection settings
    mysql_host: str = "192.168.1.25"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "qlikbiz"

    cache_ttl_hours: int = 168
    max_concurrent_requests: int = 10
    retry_attempts: int = 3
    api_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    max_bulk_urls: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
