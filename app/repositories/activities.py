from app.models.activities import ActivityDB
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class ActivityRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_activity_by_id(self, activity_id: int):
        return self.db.query(ActivityDB).filter(
            ActivityDB.id == activity_id,
        ).first()

    def get_activity_by_lead_id(self, lead_id: int):
        return self.db.query(ActivityDB).filter(
            ActivityDB.lead_id == lead_id,
        ).all()
    
    def get_activity_by_user_id(self, user_id: int):
        return self.db.query(ActivityDB).filter(
            ActivityDB.user_id == user_id
        ).all()


    def get_my_activities(self, user_id: int):
        return self.db.query(ActivityDB).filter(ActivityDB.user_id == user_id).all()


    def create_activity(self, user_id: int, data):
        activity = ActivityDB(
            lead_id=data.lead_id,
            user_id=user_id,
            description=data.description,
            activity_type=data.activity_type,
            done_at=data.done_at,
        )
        try:
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def update_activity(self, activity):
        try:
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            return activity
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def delete_activity(self, activity):
        try:
            self.db.delete(activity)
            self.db.commit()
            return activity
        except IntegrityError as e:
            self.db.rollback()
            raise e
