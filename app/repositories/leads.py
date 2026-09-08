from app.models.leads import LeadsDB
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

class LeadsRepository:
    def __init__(self, db : Session):
        self.db = db

    def get_leads_query(self, user_id: int = None):
        query = self.db.query(LeadsDB)

        if user_id is not None:
            query = query.filter(LeadsDB.user_id == user_id)
        
        return query.all()
    


    def get_lead_by_id(self, lead_id: int):
        return self.db.query(LeadsDB).filter(
            LeadsDB.id == lead_id,
).first()

    def create_lead(self, user_id: int, data):
        lead = LeadsDB(
            name=data.name,
            email=data.email,
            phone=data.phone,
            company_id=data.company_id,
            subject=data.subject,
            description=data.description,
            estimated_value=data.estimated_value,
            status=data.status,
            user_id=user_id,
        )
        try:
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            return lead
        except IntegrityError as e:
            self.db.rollback()
            raise e
    

    def get_leads_by_user_id(self, user_id: int):
        return self.db.query(LeadsDB).filter(
            LeadsDB.user_id == user_id,
            LeadsDB.is_active == True
).all()


    def get_lead_by_email(self, email: str):
        return self.db.query(LeadsDB).filter(
            LeadsDB.email == email,
).first()
    
    def get_lead_by_name(self, name: str):
        return self.db.query(LeadsDB).filter(
            LeadsDB.name == name,
).first()
    
    def get_lead_by_company_id(self, company_id: int):
        return self.db.query(LeadsDB).filter(
            LeadsDB.company_id == company_id,
).all()


    def get_all_leads(self, user_id: int = None):
        query = self.db.query(LeadsDB).filter(
            LeadsDB.is_active == True
        )

        if user_id is not None:
            query = query.filter(
                LeadsDB.user_id == user_id,
            )

        return query.all()



    def get_leads_by_status(self, status: str, user_id: int = None):
        query = self.db.query(LeadsDB).filter(
            LeadsDB.status == status,
            LeadsDB.is_active == True
        )
        
        if user_id is not None:
            query = query.filter(LeadsDB.user_id == user_id)
        
        return query.all()





    # Atualização dos Leads





    def update_lead(self, lead):


        try:
            self.db.add(lead)
            self.db.commit()
            self.db.refresh(lead)
            return lead
        except IntegrityError as e:
            self.db.rollback()
            raise e




    # Deletação dos Leads





    def delete_lead(self, lead):

        try:
            self.db.delete(lead)
            self.db.commit()
            return lead
        except IntegrityError as e:
            self.db.rollback()
            raise e
