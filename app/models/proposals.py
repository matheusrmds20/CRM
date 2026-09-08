from sqlalchemy import Column, Integer, ForeignKey, DateTime, Numeric, Enum
from sqlalchemy.orm import relationship
from app.db.base import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum


class StatusProposal(str, PyEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class ProposalDB(Base):
    __tablename__ = "proposals" 

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Enum(StatusProposal), default=StatusProposal.PENDING, nullable=False)
    value = Column(Numeric(10, 2), nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    lead = relationship("LeadsDB", back_populates="proposals")
    users = relationship("UserDB", back_populates="proposals")
