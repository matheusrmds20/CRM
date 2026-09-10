from fastapi import APIRouter, Depends
from app.services.activities import ActivityService
from app.schemas.activities import ActivityCreate, ActivityResponse, ActivityUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_activities = APIRouter(prefix="/activities", tags=["activities"])

def get_activity_service(db: Session = Depends(get_db)):
    return ActivityService(db)

@router_activities.post(
    "/create",
    response_model=ActivityResponse,
    summary="Cria uma nova atividade",
    description="Cria uma atividade associada ao usuário autenticado.",
)
def create_activity(
    data: ActivityCreate,
    service: ActivityService = Depends(get_activity_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.create_activity(current_user, data)


@router_activities.get(
    "/lead_id/{lead_id}",
    response_model=list[ActivityResponse],
    summary="Busca atividades por lead",
    description="Retorna as atividades de um lead específico.",
)
def get_activity_by_lead_id(
    lead_id: int,
    service: ActivityService = Depends(get_activity_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_activity_by_lead_id(current_user, lead_id)        

@router_activities.patch(
    "/update/{activity_id}",
    response_model=ActivityResponse,
    summary="Atualiza uma atividade",
    description="Atualiza os dados da atividade do usuário autenticado.",
)
def update_activity(
    activity_id: int,
    data: ActivityUpdate,
    service: ActivityService = Depends(get_activity_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_activity(activity_id, current_user, data)

@router_activities.delete(
    "/delete/{activity_id}",
    response_model=ActivityResponse,
    summary="Remove uma atividade",
    description="Remove a atividade do usuário autenticado pelo ID.",
)
def delete_activity(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.delete_activity(activity_id, current_user)
