"""应用配置"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "体温单回传适配平台"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 平台数据库
    PLATFORM_MONGO_URI: str = "mongodb://localhost:27017"
    PLATFORM_DB_NAME: str = "temp_adapt_platform"

    # SmartCare 默认数据库
    SMARTCARE_MONGO_URI: str = "mongodb://localhost:27017"
    SMARTCARE_DB_NAME: str = "SmartCare"

    # 加密密钥
    ENCRYPT_KEY: str = "icu-adapt-platform-key-2026!"

    # 日志
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
