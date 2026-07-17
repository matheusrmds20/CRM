from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.proposals import StatusProposalDB


class ProposalBase(BaseModel):
    lead_id: int
    status: StatusProposalDB = Field(default=StatusProposalDB.PENDING)
    value: float = Field(ge=0)
    sent_at: datetime | None = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    lead_id: int | None = None
    status: StatusProposalDB | None = None
    value: float | None = Field(default=None, ge=0)
    sent_at: datetime | None = None


class ProposalResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    status: StatusProposalDB
    value: float
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
