from app.repositories.leads import LeadsRepository
from app.schemas.leads import LeadCreate, LeadUpdate
from sqlalchemy.orm import Session
from app.api.exceps import ItemNotFoundError, ItemAlreadyExistsError, BadRequestError, NoPermissionError, UnauthorizedError


class LeadsService:
    def __init__(self, db: Session):
        self.repository = LeadsRepository(db)

    def create_lead(self, user, data: LeadCreate):
        lead_already_exists = self.repository.get_lead_by_email(data.email, user.id)

        if lead_already_exists:
            raise ValueError("Lead ja existe")

        if data.name == "":
            raise BadRequestError("Nenhum nome foi preenchido")
        
        if data.email == "":
            raise BadRequestError("Nenhum email foi preenchido")
        

        new_lead = self.repository.create_lead(user.id, data)

        return new_lead

    def list_leads(self, user):
        leads = self.repository.get_all_leads(user.id)

        if leads.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")

        if not leads:
            raise ValueError("Nenhum lead encontrado")
        
        return leads

    def list_lead_by_id(self, lead_id: int, user):
        lead = self.repository.get_lead_by_id(lead_id, user.id)
    
        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")

        if not lead:
            raise ValueError("Nenhum lead encontrado")
        return lead

    def list_lead_by_email(self, email: str, user):
        lead = self.repository.get_lead_by_email(email, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")

        if not lead:
            raise ValueError("Nenhum lead encontrado")
        return lead

    def list_lead_by_name(self, name: str, user):
        lead = self.repository.get_lead_by_name(name, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")   
        
        if not lead:
            raise ValueError("Nenhum lead encontrado")
        
        return lead

    def list_leads_by_company_id(self, company_id: int, user):
        lead = self.repository.get_lead_by_company_id(company_id, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")
        
        if not lead:
            raise ValueError("Nenhum lead encontrado")
        return lead

    def list_leads_by_status(self, status: str, user):
        lead = self.repository.get_leads_by_status(status, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise UnauthorizedError("Voce nao tem permissao para executar essa acao")

        if not lead:
            raise ValueError("Nenhum lead encontrado")
        return lead

    def update_lead(self, lead_id: int, user, data: LeadUpdate):
        lead = self.repository.get_lead_by_id(lead_id, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not lead:
            raise ValueError("Nenhum lead encontrado")
        
        if data.name == "":
            raise BadRequestError("Nenhum nome foi preenchido")
        
        if data.email == "":
            raise BadRequestError("Nenhum email foi preenchido")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)

        updated_lead = self.repository.update_lead(lead)
        return updated_lead

    def delete_lead(self, lead_id: int, user):
        lead = self.repository.get_lead_by_id(lead_id, user.id)

        if lead.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")
        
        if not lead:
            raise ValueError("Nenhum lead encontrado")

        to_delete = self.repository.delete_lead(lead)
        return to_delete
