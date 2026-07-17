from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from sqlalchemy.exc import IntegrityError
from app.core.security import hash_password

class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_id(self, user_id: int):
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()
    
    def get_user_by_username(self, username: str):
        return self.db.query(UserDB).filter(UserDB.username == username).first()
    
    def create_user(self, data):

        user = UserDB(
            username=data.username.lower(),
            hashed_password=hash_password(data.password),
            role=data.role,
            is_superuser=data.is_superuser,
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
    