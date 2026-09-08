from fastapi import APIRouter, Depends
from app.services.leads import LeadsService
from app.schemas.leads import LeadCreate, LeadResponse, LeadUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.schemas.pagination import PaginationResponse


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
    "/list/query",
    response_model=PaginationResponse[LeadResponse],
    summary="Lista leads paginados",
    description="Retorna leads paginados do usuário autenticado.",
)
def get_all_leads_query(
    page: int = 1,
    page_size: int = 10,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_leads_paginated(current_user, page, page_size)


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


@router_leads.get(
    "/list/id/{lead_id}",
    response_model=LeadResponse,
    summary="Busca lead por ID",
    description="Retorna o lead correspondente ao ID informado.",
)
def get_lead(
    lead_id: int,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_lead_by_id(lead_id, current_user)


@router_leads.get(
    "/list/email/{email}",
    response_model=LeadResponse,
    summary="Busca lead por email",
    description="Retorna o lead correspondente ao email informado.",
)
def get_lead_by_email(
    email: str,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_lead_by_email(email, current_user)


@router_leads.get(
    "/list/name/{name}",
    response_model=LeadResponse,
    summary="Busca lead por nome",
    description="Retorna o lead correspondente ao nome informado.",
)
def get_lead_by_name(
    name: str,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_lead_by_name(name, current_user)


@router_leads.get(
    "/list/company/{company_id}",
    response_model=list[LeadResponse],
    summary="Lista leads por empresa",
    description="Retorna os leads da empresa informada.",
)
def get_lead_by_company_id(
    company_id: int,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_leads_by_company_id(company_id, current_user)


@router_leads.get(
    "/list/status/{status}",
    response_model=list[LeadResponse],
    summary="Lista leads por status",
    description="Retorna os leads com o status informado.",
)    
def get_leads_by_status(
    status: str,
    service: LeadsService = Depends(get_leads_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_leads_by_status(status, current_user)

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
