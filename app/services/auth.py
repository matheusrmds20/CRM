from app.core.security import verify_password, create_access_token
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from fastapi import Depends
from app.repositories.auth import AuthRepository
from app.schemas.users import UserCreate
from app.repositories.users import UserRepository
from app.api.exceps import LoginError, NoPermissionError, ItemAlreadyExistsError, BadRequestError, ItemNotFoundError
from app.models.users import Roles

class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.auth_repository = AuthRepository(db)
        self.user_repository = UserRepository(db)

    def register_user(self, data: UserCreate):
        user_already_exists = self.auth_repository.get_user_by_username(data.username)

        if user_already_exists:
            raise ItemAlreadyExistsError("Usuario ja existe")
        
        if data.role not in [Roles.ADMIN, Roles.MANAGER, Roles.SALES]:
            raise BadRequestError("Nenhum tipo de role foi selecionado") 
        
        if data.username == "":
            raise BadRequestError("Nenhum nome foi preenchido")
        
        new_user = self.auth_repository.create_user(data)

        return new_user

    def authenticate_user(self, form_data: OAuth2PasswordRequestForm = Depends()):
        user = self.auth_repository.get_user_by_username(form_data.username)
        if not user:
            raise ItemNotFoundError("Usuário nao encontrado")
        
        if form_data.username == "":
            raise BadRequestError("Nenhum nome foi preenchido")

        if user.is_active is False:
            raise LoginError("Usuário desativado")

        if not verify_password(form_data.password, user.hashed_password):
            raise LoginError("Senha incorreta")

        token = create_access_token(data={"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
