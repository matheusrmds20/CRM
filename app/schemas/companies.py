from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CompanyBase(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    cnpj: str = Field(
        min_length=18,
        max_length=18,
        pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
    )


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    cnpj: str | None = Field(
        default=None,
        min_length=18,
        max_length=18,
        pattern=r'^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$',
    )


class CompanyResponse(BaseModel):
    id: int
    name: str
    cnpj: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
