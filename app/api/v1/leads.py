from fastapi import APIRouter, Depends
from app.services.leads import LeadsService
from app.schemas.leads import LeadCreate, LeadResponse, LeadUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session


router_leads = APIRouter(prefix="/leads", tags=["leads"])


def get_leads_service(db: Session = Depends(get_db)):
    return LeadsService(db)



@router_leads.post(
    "/create",
    response_model=LeadResponse,
    summary="Cria um novo lead",
    description="Cria um lead associado ao usuário autenticado.",
)
def create_lead(
    data: LeadCreate,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.create_lead(current_user, data)


@router_leads.get(
    "",
    response_model=list[LeadResponse],
    summary="Lista todos os leads",
    description="Retorna todos os leads do usuário autenticado.",
)
def get_all_leads(
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):


    return service.get_all_leads(current_user)


@router_leads.patch(
    "/update/{lead_id}",
    response_model=LeadResponse,
    summary="Atualiza um lead",
    description="Atualiza os dados do lead do usuário autenticado.",
)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_lead(lead_id, current_user, data)


@router_leads.delete(
    "/delete/{lead_id}",
    response_model=LeadResponse,
    summary="Remove um lead",
    description="Remove o lead do usuário autenticado pelo ID.",
)
def delete_lead(
    lead_id: int,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.delete_lead(lead_id, current_user)
