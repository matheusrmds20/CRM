from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

_COMPROMISED_SECRET_KEY = "6f6b01126b4312d73bdeceaf2fdf27b88ab2f72beb115fa3a3ce9b3e47701adc"

class Settings(BaseSettings):
    APP_NAME: str = "CRM de vendas"
    DEBUG: bool = False

    SECRET_KEY: str = Field(min_length=32)

    @field_validator("SECRET_KEY")
    @classmethod
    def rejeitar_chave_comprometida(cls, valor: str) -> str:
        if valor == _COMPROMISED_SECRET_KEY:
            raise ValueError("SECRET_KEY comprometida: gere uma nova chave")
        return valor
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    CORS_ORIGINS: Annotated[list[str], NoDecode] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def separar_origens_por_virgula(cls, valor) -> list[str]:
        """Aceita lista JSON (pydantic default) ou string separada por vírgula."""
        if isinstance(valor, str):
            return [item.strip() for item in valor.split(",") if item.strip()]
        return valor

    model_config=SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
        )

    DATABASE_URL: str

@lru_cache
def get_settings():
    return Settings()