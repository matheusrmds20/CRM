from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum 
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base
from enum import Enum as PyEnum


class Roles(str, PyEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    SALES = "sales"                


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    role = Column(Enum(Roles), default=Roles.SALES, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now() , nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    leads = relationship("LeadsDB", back_populates="users", cascade="all, delete-orphan")
    proposals = relationship("ProposalDB", back_populates="users", cascade="all, delete-orphan")
    activities = relationship("ActivityDB", back_populates="users", cascade="all, delete-orphan")