from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from validate_docbr import CNPJ
from pydantic import field_validator
import re

def validate_cnpj(cnpj) -> str:
    """Normaliza e valida o CNPJ; validacao defensiva para nunca estourar 500."""
    if not isinstance(cnpj, str):
        raise ValueError("CNPJ inválido")

    cleaned = re.sub(r'[^\d]', '', cnpj)

    cnpj_validater = CNPJ()
    try:
        is_valid = cnpj_validater.validate(cleaned)
    except Exception:
        is_valid = False
    if not is_valid:
        raise ValueError("CNPJ inválido")

    return cnpj_validater.mask(cleaned)

class CompanyBase(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    cnpj: str
    is_active: bool = True

    @field_validator("cnpj")
    @classmethod
    def cnpj_validator(cls, cnpj):
        return validate_cnpj(cnpj)

class CompanyCreate(CompanyBase):
    pass

class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    cnpj: str | None = Field(default=None, min_length=14, max_length=18)
    is_active: bool | None = None

    @field_validator("cnpj")
    @classmethod
    def cnpj_validator(cls, cnpj):

        if cnpj is None:
            return None
        return validate_cnpj(cnpj)

class CompanyResponse(BaseModel):
    id: int
    name: str
    cnpj: str
    is_active: bool
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)