from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field
from app.models.proposals import StatusProposal


class ProposalBase(BaseModel):
    lead_id: int
    status: StatusProposal = Field(default=StatusProposal.PENDING)
    value: Decimal = Field(ge=0, decimal_places=2)
    sent_at: datetime | None = None


class ProposalCreate(ProposalBase):
    pass


class ProposalUpdate(BaseModel):
    status: StatusProposal | None = None
    value: float | None = Field(default=None, ge=0)
    sent_at: datetime | None = None


class ProposalResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    status: StatusProposal
    value: float
    sent_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
