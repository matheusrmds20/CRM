from pydantic import BaseModel, Field, ConfigDict, EmailStr, field_validator
from app.models.leads import StatusLeads
from datetime import datetime
from typing import Optional



class LeadBase(BaseModel):
    name: str = Field(min_length=3, max_length=20)
    email: EmailStr
    phone: str | None = Field(min_length=3, max_length=20)
    company_id: int | None 
    subject: str = Field(min_length=3, max_length=20)
    description: str | None = Field(min_length=3, max_length=20)
    estimated_value: float | None = Field(ge=0)
    status: StatusLeads = Field(default=StatusLeads.NEW)

    @field_validator("company_id", mode="before")
    @classmethod
    def zero_to_none(cls, value):
        return None if value == 0 else value

class LeadCreate(LeadBase):
    pass

class LeadUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    company_id: int | None
    status: StatusLeads | None = None
    subject: str | None = None
    description: str | None = None
    estimated_value: float | None = None
    is_active: bool | None = None

    @field_validator("company_id", mode="before")
    @classmethod
    def zero_to_none(cls, value):
        return None if value == 0 else value

class LeadResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str | None
    company_id: int | None
    user_id: int
    subject: str
    description: str | None
    estimated_value: float | None
    status: str
    created_at: datetime
    updated_at: datetime | None


    model_config = ConfigDict(from_attributes=True)

    