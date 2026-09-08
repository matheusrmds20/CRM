from app.repositories.companies import CompanyRepository
from sqlalchemy.orm import Session
from app.schemas.companies import CompanyCreate, CompanyUpdate
from app.api.exceps import ItemNotFoundError, ItemAlreadyExistsError, BadRequestError, NoPermissionError
from app.utils.permissions import can_manage_admin

class CompanyService:
    def __init__(self, db: Session):
        self.repository = CompanyRepository(db)



    def create_company(self, user, data: CompanyCreate):
        company_already_exists = self.repository.get_company_by_cnpj(data.cnpj)

        if company_already_exists:
            raise ItemAlreadyExistsError("Company já existe")

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        data.name = data.name.lower()
 
        new_company = self.repository.create_company(data)

        return new_company
    
    def get_company_by_id(self, company_id: int):
        company = self.repository.get_company_by_id(company_id)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")
        
        return company

    def get_company_by_cnpj(self, cnpj: str):
        company = self.repository.get_company_by_cnpj(cnpj)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        return company

    def get_company_by_name(self, name: str):
        company = self.repository.get_company_by_name(name)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        return company
    
    def get_all_companies(self, user):
        companies = self.repository.get_all_companies()

        if not companies:
            raise ItemNotFoundError("Nenhum company encontrado")

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")
        
        
        return companies


    def update_company(self, user, company_id: int, data: CompanyUpdate):
        company = self.repository.get_company_by_id(company_id)


        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        updated_company = self.repository.update_company(company)

        return updated_company
    
    def delete_company(self, user, company_id: int):
        company = self.repository.get_company_by_id(company_id)

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        to_delete = self.repository.delete_company(company)

        return to_delete
