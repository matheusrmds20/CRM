from pydantic import BaseModel, Field, ConfigDict
from app.models.users import Roles
from datetime import datetime


class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=120)
    role: Roles = Field(default=Roles.SALES)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    pass


class UserUpdateUsername(BaseModel):
    username: str = Field(min_length=3, max_length=20)

    model_config = ConfigDict(from_attributes=True)

class UserUpdatePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=20)
    new_password: str = Field(min_length=8, max_length=20)

    model_config = ConfigDict(from_attributes=True)

class UserResponse(BaseModel):
    id: int
    role: Roles
    username: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=20)
    password: str = Field(min_length=8, max_length=20)

    model_config = ConfigDict(from_attributes=True)