from app.repositories.leads import LeadsRepository
from app.schemas.leads import LeadCreate, LeadUpdate
from sqlalchemy.orm import Session
from app.api.exceps import ItemNotFoundError, BadRequestError, NoPermissionError, ItemAlreadyExistsError
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


    def get_all_leads(self, user, user_id: int = None):


        if user.role in ("admin", "manager"):
            leads = self.repository.get_all_leads(user_id)
        else:
            leads = self.repository.get_all_leads(user.id)

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
