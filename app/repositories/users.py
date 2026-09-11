from app.models.users import UserDB
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_me(self, user_id: int):
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()

    def get_all_users(self):
        return self.db.query(UserDB).all()

    def get_user_by_id(self, user_id: int):
        return self.db.query(UserDB).filter(UserDB.id == user_id).first()
    
    def get_user_by_username(self, username: str):
        return self.db.query(UserDB).filter(UserDB.username == username).first()

        
    def update_username(self, user_id: int, new_username: str):
        user = self.get_user_by_id(user_id)


        user.username = new_username

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def update_user(self, user_id: int, username: str, role):
        user = self.get_user_by_id(user_id)
        user.username = username
        user.role = role

        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise e
        
    def update_password(self, user_id: int, new_password: str):
        user = self.get_user_by_id(user_id)
        user.hashed_password = new_password
        
        try:
            self.db.commit()
            self.db.refresh(user)
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise e

    def delete_user(self, user):
        try:
            self.db.delete(user)
            self.db.commit()
            return user
        except IntegrityError as e:
            self.db.rollback()
            raise e 
