from app.repositories.users import UserRepository
from app.schemas.users import UserUpdateUsername, UserUpdatePassword
from sqlalchemy.orm import Session
from app.api.exceps import BadRequestError, NoPermissionError
from app.core.security import verify_password


class UserService:
    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def update_username(self, user, data: UserUpdateUsername):
        user_repo = self.repository.get_user_by_id(user.id)

        if not user_repo:
            raise BadRequestError("Usuario nao encontrado")

        if user.id != user_repo.id:
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if data.username == "":
            raise BadRequestError("Nenhum nome de usuario foi selecionado")

        return self.repository.update_username(user.id, data.username)

    def update_password(self, user, data: UserUpdatePassword):
        user_repo = self.repository.get_user_by_id(user.id)

        if not user_repo:
            raise BadRequestError("Usuario nao encontrado")

        if user.id != user_repo.id:
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if data.new_password == "":
            raise BadRequestError("Nenhuma senha foi selecionada")

        if data.current_password == "":
            raise BadRequestError("Nenhuma senha atual foi selecionada")

        if not verify_password(data.current_password, user_repo.hashed_password):
            raise BadRequestError("Senha atual incorreta")

        return self.repository.update_password(user.id, data.new_password)
