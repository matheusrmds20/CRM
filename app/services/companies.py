from app.repositories.companies import CompanyRepository
from app.repositories.leads import LeadsRepository
from sqlalchemy.orm import Session
from app.schemas.companies import CompanyCreate, CompanyUpdate
from app.api.exceps import ItemNotFoundError, ItemAlreadyExistsError, BadRequestError, NoPermissionError
from app.utils.permissions import can_manage_admin, can_manage_manager

class CompanyService:
    def __init__(self, db: Session):
        self.repository = CompanyRepository(db)
        self.leads_repository = LeadsRepository(db)

    def create_company(self, user, data: CompanyCreate):
        company_already_exists = self.repository.get_company_by_cnpj(data.cnpj)

        if company_already_exists:
            raise ItemAlreadyExistsError("Company já existe")

        if not can_manage_manager(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        data.name = data.name.lower()

        new_company = self.repository.create_company(data)

        return new_company

    def get_all_companies(self, user):

        return self.repository.get_all_companies()

    def update_company(self, user, company_id: int, data: CompanyUpdate):
        company = self.repository.get_company_by_id(company_id)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        if not can_manage_manager(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        for field, value in data.model_dump(exclude_unset=True).items():
            if value is None:
                continue
            setattr(company, field, value)

        updated_company = self.repository.update_company(company)

        return updated_company

    def delete_company(self, user, company_id: int):
        company = self.repository.get_company_by_id(company_id)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        if not can_manage_manager(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if self.leads_repository.count_by_company_id(company_id) > 0:
            raise BadRequestError("Existem leads vinculados a esta empresa")

        to_delete = self.repository.delete_company(company)

        return to_delete