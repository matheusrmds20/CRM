from app.repositories.companies import CompanyRepository
from sqlalchemy.orm import Session
from app.schemas.companies import CompanyCreate, CompanyUpdate
from app.api.exceps import ItemNotFoundError, ItemAlreadyExistsError, BadRequestError, NoPermissionError, UnauthorizedError


class CompanyService:
    def __init__(self, db: Session):
        self.repository = CompanyRepository(db)

    def create_company(self, user, data: CompanyCreate):
        company_already_exists = self.repository.get_company_by_cnpj(data.cnpj)

        if user.role != "admin":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if company_already_exists:
            raise ItemAlreadyExistsError("Company já existe")

        if data.name == "":
            raise BadRequestError("Nenhum nome foi preenchido")
        
        if data.cnpj == "":
            raise BadRequestError("Nenhum cnpj foi preenchido")
        
 

        new_company = self.repository.create_company(data)

        return new_company
    
    def get_company_by_id(self, user, company_id: int):
        company = self.repository.get_company_by_id(company_id)

        if company.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not company:
            raise ItemNotFoundError("Nenhum company encontrado")
        
        return company

    def get_company_by_cnpj(self, user, cnpj: str):
        company = self.repository.get_company_by_cnpj(cnpj)

        if company.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not company:
            raise ValueError("Nenhum company encontrado")
     
        return company

    def get_company_by_name(self, user, name: str):
        company = self.repository.get_company_by_name(name)

        if company.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not company:
            raise ValueError("Nenhum company encontrado")
        

        
        return company
    
    def get_all_companies(self, user):
        companies = self.repository.get_all_companies()

        if companies.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not companies:
            raise ValueError("Nenhum company encontrado")
        
        
        return companies


    def update_company(self, user, company_id: int, data: CompanyUpdate):
        company = self.repository.get_company_by_id(company_id)

        if company.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not company:
            raise ValueError("Nenhum company encontrado")
        
        if data.cnpj == "":
            raise BadRequestError("Nenhum cnpj foi preenchido")
        
        if data.name == "":
            raise BadRequestError("Nenhum nome foi preenchido")

        
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(company, field, value)

        updated_company = self.repository.update_company(company)

        return updated_company
    
    def delete_company(self, user, company_id: int):
        company = self.repository.get_company_by_id(company_id)
    
        if company.user_id != user.id and user.role != "admin" and user.role != "manager":
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not company:
            raise ValueError("Nenhum company encontrado")

        
        to_delete = self.repository.delete_company(company)

        return to_delete