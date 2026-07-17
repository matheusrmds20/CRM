from fastapi import APIRouter, Depends
from app.services.activities import ActivityService
from app.schemas.activities import ActivityCreate, ActivityResponse, ActivityUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_activities = APIRouter(prefix="/activities", tags=["activities"])

@router_activities.post("/create", response_model=ActivityResponse)
def create_activity(
    data: ActivityCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.create_activity(current_user.id, data)

@router_activities.get("", response_model=list[ActivityResponse])
def get_all_activities(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.get_all_activities(current_user)
    
@router_activities.get("/id/{activity_id}", response_model=ActivityResponse)
def get_activity_by_id(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.get_activity_by_id(current_user, activity_id)

@router_activities.get("/lead_id/{lead_id}", response_model=ActivityResponse)
def get_activity_by_lead_id(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.get_activity_by_lead_id(current_user, lead_id)        

@router_activities.get("/user_id/{user_id}", response_model=list[ActivityResponse])
def get_activity_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)   

    return service.get_activity_by_user_id(current_user, user_id)

@router_activities.patch("/{activity_id}", response_model=ActivityUpdate)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.update_activity(activity_id, current_user, data)

@router_activities.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ActivityService(db)

    return service.delete_activity(activity_id, current_user)