from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from validate_docbr import CNPJ
from pydantic import field_validator
import re

class CompanyBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    cnpj: str
    is_active: bool = True

    @field_validator("cnpj")
    def cnpj_validator(cls, cnpj):
        cleaned = re.sub(r'[^\d]', '', cnpj)

        cnpj_validater = CNPJ()
        if not cnpj_validater.validate(cleaned):
            raise ValueError("CNPJ inválido")

        return cnpj_validater.mask(cleaned)

class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)

    @field_validator("cnpj")
    @classmethod
    def cnpj_validator(cls, cnpj):
        cleaned = re.sub(r'[^\d]', '', cnpj)

        cnpj_validater = CNPJ()
        if not cnpj_validater.validate(cleaned):
            raise ValueError("CNPJ inválido")

        return cnpj_validater.mask(cleaned)

class CompanyResponse(BaseModel):
    id: int
    name: str
    cnpj: str
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
