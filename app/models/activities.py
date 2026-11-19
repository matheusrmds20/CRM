from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum


class ActivityType(str, PyEnum):
    CALL = "call"
    MEETING = "meeting"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    OTHER = "other"


class ActivityDB(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    description = Column(String, nullable=False)
    activity_type = Column(Enum(ActivityType), default=ActivityType.CALL, nullable=False)
    done_at = Column(DateTime(timezone=True), nullable=True, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lead = relationship("LeadsDB", back_populates="activities")
    users = relationship("UserDB", back_populates="activities")
