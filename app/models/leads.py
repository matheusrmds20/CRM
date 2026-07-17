from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Float, Enum
from sqlalchemy.orm import relationship
from app.db.database import Base
from sqlalchemy.sql import func
from enum import Enum as PyEnum



class StatusLeads(str, PyEnum):
    NEW = "new"
    CONTACTED = "contacted"
    LOST = "lost"
    WON = "won"


class LeadsDB(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=True)
    status = Column(Enum(StatusLeads), default=StatusLeads.NEW, nullable=False)
    subject = Column(String, nullable=False)
    description = Column(String, nullable=True)
    estimated_value = Column(Float, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    


    user = relationship("UserDB", back_populates="leads")
    company = relationship("CompanyDB", back_populates="leads")
    activities = relationship("ActivityDB", back_populates="lead")
    proposals = relationship("ProposalDB", back_populates="lead")