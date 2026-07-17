from sqlalchemy.orm import Session
from app.models.companies import CompanyDB
from sqlalchemy.exc import IntegrityError


class CompanyRepository:
    def __init__(self, db: Session):
        self.db = db
        
        
    def get_company_by_id(self, company_id: int):
        return self.db.query(CompanyDB).filter(CompanyDB.id == company_id).first()

    def get_company_by_cnpj(self, cnpj: str):
        return self.db.query(CompanyDB).filter(CompanyDB.cnpj == cnpj).first()

    def get_company_by_name(self, name: str):
        return self.db.query(CompanyDB).filter(CompanyDB.name == name).first()
    
    def get_all_companies(self):
        return self.db.query(CompanyDB).all()


    def create_company(self, data):

        company = CompanyDB(
            name=data.name.lower(),
            cnpj=data.cnpj,
        )
        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except IntegrityError as e:
            self.db.rollback()
            raise e
        
    def update_company(self, company):
        try:
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
            return company
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def delete_company(self, company):
        try:
            self.db.delete(company)
            self.db.commit()
            return company
        except IntegrityError as e:
            self.db.rollback()