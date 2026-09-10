from app.repositories.leads import LeadsRepository
from app.schemas.leads import LeadCreate, LeadUpdate
from sqlalchemy.orm import Session
from app.api.exceps import ItemNotFoundError, BadRequestError, NoPermissionError, ItemAlreadyExistsError
from app.utils.pagination import paginate
from app.utils.permissions import can_manage, can_manage_admin


class LeadsService:
    def __init__(self, db: Session):
        self.repository = LeadsRepository(db)

    def create_lead(self, user, data: LeadCreate):
        lead_already_exists = self.repository.get_lead_by_email(data.email)
        if lead_already_exists:
            raise ItemAlreadyExistsError("Lead ja existe")

        data.name = data.name.lower()

        return self.repository.create_lead(user.id, data)

    def get_leads_paginated(self, user, page: int = 1, page_size: int = 10):

        if can_manage_admin(user):
            query = self.repository.get_all_leads()
        else:
            query = self.repository.get_all_leads(user.id)


        return paginate(query, page, page_size)

    def get_all_leads(self, user, user_id: int = None):
        if user.role in ("admin", "manager"):
            leads = self.repository.get_all_leads(user_id)
        else:
            leads = self.repository.get_all_leads(user.id)


        return leads

    def get_lead_by_id(self, lead_id: int, user):
        lead = self.repository.get_lead_by_id(lead_id)


        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return lead

    def get_lead_by_email(self, email: str, user):
        lead = self.repository.get_lead_by_email(email)



        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return lead

    def get_lead_by_name(self, name: str, user):
        lead = self.repository.get_lead_by_name(name)

        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return lead

    def get_leads_by_company_id(self, company_id: int, user):
        leads = self.repository.get_lead_by_company_id(company_id)

        if not all(can_manage(user, lead.user_id) for lead in leads):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return leads

    def get_leads_by_status(self, status: str, user, user_id: int = None):
        if status not in ("new", "contacted", "lost", "won"):
            raise BadRequestError("Status invalido")

        if user.role in ("admin", "manager"):
            target_user_id = user_id
        else:
            target_user_id = user.id if user_id is None else user_id

        leads = self.repository.get_leads_by_status(status, target_user_id)


        if not all(can_manage(user, lead.user_id) for lead in leads):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return leads

    def update_lead(self, lead_id: int, user, data: LeadUpdate):
        lead = self.repository.get_lead_by_id(lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)

        return self.repository.update_lead(lead)

    def delete_lead(self, lead_id: int, user):
        lead = self.repository.get_lead_by_id(lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_lead(lead)
