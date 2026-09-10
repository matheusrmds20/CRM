from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "CRM de vendas"
    DEBUG: bool = False

    

    SECRET_KEY: str = Field(default="6f6b01126b4312d73bdeceaf2fdf27b88ab2f72beb115fa3a3ce9b3e47701adc", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config=SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
        )

    DATABASE_URL: str 

@lru_cache
def get_settings():
    return Settings()