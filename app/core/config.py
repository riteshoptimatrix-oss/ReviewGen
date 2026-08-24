from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL
from typing import Optional

class Settings(BaseSettings):
    debug_extraction: bool = False
    http_timeout_seconds: int = 20
    max_redirects: int = 10

    # MySQL connection settings
    mysql_host: str = "localhost"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = ""
    mysql_db: str = "business_cache"
    mysql_charset: str = "utf8mb4"

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="mysql+aiomysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_db,
            query={"charset": self.mysql_charset},
        )

    cache_ttl_hours: int = 168
    max_concurrent_requests: int = 10
    retry_attempts: int = 3
    api_key: Optional[str] = None
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    max_bulk_urls: int = 100

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
