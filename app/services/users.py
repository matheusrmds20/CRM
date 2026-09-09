from app.repositories.users import UserRepository
from app.schemas.users import UserUpdate, UserUpdateUsername, UserUpdatePassword, UserCreate
from sqlalchemy.orm import Session
from app.api.exceps import BadRequestError, NoPermissionError, ItemNotFoundError
from app.core.security import verify_password, hash_password
from app.utils.permissions import can_manage
from app.utils.permissions import can_manage_admin


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def create_user(self, user, data: UserCreate):
        user_repo = self.repository.get_user_by_username(data.username)

        if user_repo:
            raise BadRequestError("Usuário ja existente")

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        data.password = hash_password(data.password)

        return self.repository.create_user(data)

    def get_me(self, user):
        user_repo = self.repository.get_me(user.id)

        if not user_repo:
            raise ItemNotFoundError("Nenhum user encontrado")

        return user_repo

    def get_user_by_id(self, user, user_id: int):
        user_repo = self.repository.get_user_by_id(user_id)

        if not user_repo:
            raise ItemNotFoundError("Nenhum user encontrado")

        if not can_manage(user, user_repo.id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")
        
        return user_repo

    def get_user_by_username(self, user, username: str):
        user_repo = self.repository.get_user_by_username(username)

        if not user_repo:
            raise ItemNotFoundError("Nenhum user encontrado")

        if not can_manage(user, user_repo.id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return user_repo

    def get_all_users(self, user):

        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.get_all_users()



    def update_username(self, user, data: UserUpdateUsername, target_user_id: int):
        target_id = target_user_id if target_user_id is not None else user.id
        user_repo = self.repository.get_user_by_id(target_id)


        
        if not user_repo:
            raise ItemNotFoundError("Usuario nao encontrado")

        if not can_manage(user, user_repo.id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        return self.repository.update_username(target_id, data.username)

    def update_user(self, user, data: UserUpdate, target_user_id: int):
        if not can_manage_admin(user):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        user_repo = self.repository.get_user_by_id(target_user_id)
        if not user_repo:
            raise ItemNotFoundError("Usuario nao encontrado")

        existing_user = self.repository.get_user_by_username(data.username)
        if existing_user and existing_user.id != target_user_id:
            raise BadRequestError("Usuário ja existente")

        return self.repository.update_user(target_user_id, data.username, data.role)

    def update_password(self, user, data: UserUpdatePassword, target_user_id: int):
        target_id = target_user_id if target_user_id is not None else user.id
        user_repo = self.repository.get_user_by_id(target_id)

        if not user_repo:
            raise ItemNotFoundError("Usuario nao encontrado")

        if not can_manage(user, user_repo.id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if not verify_password(data.current_password, user_repo.hashed_password):
            raise BadRequestError("Senha atual incorreta")

        new_hashed_password = hash_password(data.new_password)

        return self.repository.update_password(user_repo.id, new_hashed_password)

    def delete_user(self, user, target_user_id: int = None):
        target_id = target_user_id if target_user_id is not None else user.id

        user_repo = self.repository.get_user_by_id(target_id)

        if not user_repo:
            raise ItemNotFoundError("Nenhum user encontrado")

        if not can_manage(user, user_repo.id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")
        
        return self.repository.delete_user(user_repo)
