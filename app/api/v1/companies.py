from fastapi import APIRouter, Depends
from app.services.companies import CompanyService
from app.schemas.companies import CompanyCreate, CompanyResponse, CompanyUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session


router_companies = APIRouter(prefix="/companies", tags=["companies"])

def get_company_service(db: Session = Depends(get_db)):
    return CompanyService(db)

@router_companies.post(
    "/create",
    response_model=CompanyResponse,
    summary="Cria uma nova empresa",
    description="Cria uma empresa associada ao usuário autenticado.",
)
def create_company(
    data: CompanyCreate,
    service: CompanyService = Depends(get_company_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.create_company(current_user, data)

@router_companies.get(
    "",
    response_model=list[CompanyResponse],
    summary="Lista todas as empresas",
    description="Retorna todas as empresas do usuário autenticado.",
)
def get_all_companies(
    service: CompanyService = Depends(get_company_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_all_companies(current_user)
    
@router_companies.patch(
    "/update/{company_id}",
    response_model=CompanyResponse,
    summary="Atualiza uma empresa",
    description="Atualiza os dados da empresa do usuário autenticado.",
)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    service: CompanyService = Depends(get_company_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_company(current_user, company_id, data)

@router_companies.delete(
    "/delete/{company_id}",
    response_model=CompanyResponse,
    summary="Remove uma empresa",
    description="Remove a empresa do usuário autenticado pelo ID.",
)
def delete_company(
    company_id: int,
    service: CompanyService = Depends(get_company_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.delete_company(current_user, company_id)
