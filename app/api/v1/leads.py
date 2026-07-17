from fastapi import APIRouter, Depends
from app.services.leads import LeadsService
from app.schemas.leads import LeadCreate, LeadResponse, LeadUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_leads = APIRouter(prefix="/leads", tags=["leads"])


@router_leads.post("/create_lead", response_model=LeadResponse)
def create_lead(
    data: LeadCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.create_lead(current_user, data)


@router_leads.get("/list/all", response_model=list[LeadResponse])
def get_all_leads(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_leads(current_user)


@router_leads.get("list/lead_by_id/{lead_id}", response_model=LeadResponse)
def get_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_lead_by_id(lead_id, current_user)


@router_leads.get("/list/email/{email}", response_model=LeadResponse)
def get_lead_by_email(
    email: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_lead_by_email(email, current_user)


@router_leads.get("/list/name/{name}", response_model=LeadResponse)
def get_lead_by_name(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_lead_by_name(name, current_user)


@router_leads.get("/list/company/{company_id}", response_model=LeadResponse)
def get_lead_by_company_id(
    company_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_lead_by_company_id(company_id, current_user)


@router_leads.get("/status/{status}", response_model=list[LeadResponse])    
def get_leads_by_status(
    status: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.list_leads_by_status(status, current_user)

@router_leads.patch("/update/{lead_id}", response_model=LeadResponse)
def update_lead(
    lead_id: int,
    data: LeadUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.update_lead(lead_id, current_user, data)


@router_leads.delete("/delete/{lead_id}", response_model=LeadResponse)
def delete_lead(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = LeadsService(db)

    return service.delete_lead(lead_id, current_user)
