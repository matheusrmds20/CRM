from app.models.users import UserDB
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.core.security import hash_password

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    
    def create_user(self, data):

        user = UserDB(
            username=data.username.lower(),
            hashed_password=data.password,
            role=data.role,
            is_active=data.is_active,

        )

        try:
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise e
    