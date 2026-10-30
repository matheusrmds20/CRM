from app.repositories.leads import LeadsRepository
from app.repositories.companies import CompanyRepository
from app.schemas.leads import LeadCreate, LeadUpdate
from sqlalchemy.orm import Session
from app.api.exceps import ItemNotFoundError, BadRequestError, NoPermissionError, ItemAlreadyExistsError
from app.utils.permissions import can_edit_lead, can_view_all_leads

class LeadsService:
    def __init__(self, db: Session):
        self.repository = LeadsRepository(db)
        self.company_repository = CompanyRepository(db)

    def _ensure_company_exists(self, company_id: int | None) -> None:
        """Valida que a empresa referenciada pelo lead existe no banco."""
        if company_id is None:
            return
        company = self.company_repository.get_company_by_id(company_id)
        if not company:
            raise ItemNotFoundError("Empresa nao encontrada")

    def create_lead(self, user, data: LeadCreate):
        lead_already_exists = self.repository.get_lead_by_email(data.email)
        if lead_already_exists:
            raise ItemAlreadyExistsError("Lead ja existe")

        data.name = data.name.lower()
        self._ensure_company_exists(data.company_id)

        return self.repository.create_lead(user.id, data)

    def get_all_leads(self, user, user_id: int = None):

        if can_view_all_leads(user):
            leads = self.repository.get_all_leads(user_id)
        else:
            leads = self.repository.get_all_leads(user.id)

        return leads

    def update_lead(self, lead_id: int, user, data: LeadUpdate):
        lead = self.repository.get_lead_by_id(lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_edit_lead(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        payload = data.model_dump(exclude_unset=True)
        if "company_id" in payload:
            self._ensure_company_exists(payload["company_id"])

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(lead, field, value)

        return self.repository.update_lead(lead)

    def delete_lead(self, lead_id: int, user):
        lead = self.repository.get_lead_by_id(lead_id)
        if not lead:
            raise ItemNotFoundError("Nenhum lead encontrado")

        if not can_edit_lead(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_lead(lead)