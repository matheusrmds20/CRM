from app.models.proposals import ProposalDB
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

class ProposalRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_proposal_by_id(self, proposal_id: int):
        return self.db.query(ProposalDB).filter(
            ProposalDB.id == proposal_id,
    ).first()

    def get_proposal_by_lead_id(self, lead_id: int):
        return self.db.query(ProposalDB).filter(
            ProposalDB.lead_id == lead_id,
    ).all()
    
    def create_proposal(self, user_id: int, data):
        proposal = ProposalDB(
            lead_id=data.lead_id,
            user_id=user_id,
            status=data.status,
            value=data.value,
            sent_at=data.sent_at,
        )
        try:
            self.db.add(proposal)
            self.db.commit()
            self.db.refresh(proposal)
            return proposal
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def update_proposal(self, proposal):
        try:
            self.db.add(proposal)
            self.db.commit()
            self.db.refresh(proposal)
            return proposal
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def delete_proposal(self, proposal):
        try:
            self.db.delete(proposal)
            self.db.commit()
            return proposal
        except IntegrityError as e:
            self.db.rollback()
            raise e