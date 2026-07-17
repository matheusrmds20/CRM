from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.activities import ActivityTypeDB


class ActivityBase(BaseModel):
    lead_id: int
    description: str = Field(min_length=3, max_length=500)
    type: ActivityTypeDB
    done_at: datetime | None = None


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    lead_id: int | None = None
    description: str | None = Field(default=None, min_length=3, max_length=500)
    type: ActivityTypeDB | None = None
    done_at: datetime | None = None


class ActivityResponse(BaseModel):
    id: int
    lead_id: int
    user_id: int
    description: str
    type: ActivityTypeDB
    done_at: datetime | None
    created_at: datetime
    updated_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
