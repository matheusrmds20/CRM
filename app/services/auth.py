from app.core.security import verify_password, create_access_token, hash_password
from sqlalchemy.orm import Session
from app.repositories.auth import AuthRepository
from app.schemas.users import UserCreate
from app.repositories.users import UserRepository
from app.api.exceps import LoginError, NoPermissionError, ItemAlreadyExistsError, BadRequestError, ItemNotFoundError
from app.models.users import Roles
from app.utils.permissions import can_manage_admin

class AuthService:
    def __init__(self, db: Session):
        self.auth_repository = AuthRepository(db)
        self.user_repository = UserRepository(db)

    def register_user(self, data: UserCreate, user):
        user_already_exists = self.user_repository.get_user_by_username(data.username)

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if user_already_exists:
            raise ItemAlreadyExistsError("Usuario ja existe")

        if data.role not in [Roles.ADMIN, Roles.MANAGER, Roles.SALES]:
            raise BadRequestError("Nenhum tipo de role foi selecionado")

        if data.username == "":
            raise BadRequestError("Nenhum nome foi preenchido")

        data.password = hash_password(data.password)

        new_user = self.auth_repository.create_user(data)

        return new_user

    def authenticate_user(self, form_data_username: str, form_data_password: str):
        user = self.user_repository.get_user_by_username(form_data_username)

        if not user:
            raise LoginError("Usuário ou senha incorreto")

        if user.is_active is False:
            raise LoginError("Usuário ou senha incorreto")

        if not verify_password(form_data_password, user.hashed_password):
            raise LoginError("Usuário ou senha incorreto")

        token = create_access_token(data={"sub": user.username, "ver": user.token_version})
        return {"access_token": token, "token_type": "bearer"}