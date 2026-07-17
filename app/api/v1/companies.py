from fastapi import APIRouter, Depends
from app.services.companies import CompanyService
from app.schemas.companies import CompanyCreate, CompanyResponse, CompanyUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session



router_companies = APIRouter(prefix="/companies", tags=["companies"])

@router_companies.post("/create", response_model=CompanyResponse)
def create_company(
    data: CompanyCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.create_company(current_user, data)

@router_companies.get("", response_model=list[CompanyResponse])
def get_all_companies(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.get_all_companies(current_user)
    
@router_companies.get("/id/{company_id}", response_model=CompanyResponse)
def get_company_by_id(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.get_company_by_id(current_user, company_id)

@router_companies.get("/cnpj/{cnpj}", response_model=CompanyResponse)
def get_company_by_cnpj(
    cnpj: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.get_company_by_cnpj(current_user, cnpj)

@router_companies.get("/name/{name}", response_model=CompanyResponse)
def get_company_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.get_company_by_name(current_user, name)

@router_companies.patch("/{company_id}", response_model=CompanyUpdate)
def update_company(
    company_id: int,
    data: CompanyUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.update_company(current_user, company_id, data)

@router_companies.delete("/{company_id}")
def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = CompanyService(db)

    return service.delete_company(current_user, company_id)