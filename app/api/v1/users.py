from fastapi import APIRouter, Depends
from app.services.users import UserService
from app.schemas.users import UserResponse, UserUpdate, UserUpdateUsername, UserUpdatePassword
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_user = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)


@router_user.post(
    "/create",
    response_model=UserResponse,
    summary="Cria um novo usuário",
    description="Cria um usuário associado ao usuário autenticado.",
)
def create_user(
    data: UserResponse,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    return service.create_user(current_user, data)


@router_user.get(
    "/me",
    response_model=UserResponse,
    summary="Busca dados do usuário atual",
    description="Retorna os dados do usuário autenticado.",
)
def get_me(
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    return service.get_me(current_user)

@router_user.get(
    "",
    response_model=list[UserResponse],
    summary="Lista todos os usuários",
    description="Retorna todos os usuários do usuário autenticado.",
)
def get_all_users(
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    
    return service.get_all_users(current_user)

@router_user.get(
    "/list/by_id/{user_id}",
    response_model=UserResponse,
    summary="Busca usuário por ID",
    description="Retorna o usuário correspondente ao ID informado.",
)
def get_user_by_id(
    user_id: int,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    
    return service.get_user_by_id(current_user, user_id)

@router_user.get(
    "/list/by_username/{username}",
    response_model=UserResponse,
    summary="Busca usuário por nome de usuário",
    description="Retorna o usuário correspondente ao nome de usuário informado.",
)
def get_user_by_username(
    username: str,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    
    return service.get_user_by_username(current_user, username)


@router_user.patch(
    "/update_username/{target_user_id}",
    response_model=UserResponse,
    summary="Atualiza o nome de usuário",
    description="Atualiza o nome de usuário do usuário alvo.",
)
def update_username(
    target_user_id: int,
    data: UserUpdateUsername,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_username(current_user, data, target_user_id)


@router_user.patch(
    "/update/{target_user_id}",
    response_model=UserResponse,
    summary="Atualiza um usuário",
)
def update_user(
    target_user_id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    return service.update_user(current_user, data, target_user_id)


@router_user.patch(
    "/update_password/{target_user_id}",
    response_model=UserResponse,
    summary="Atualiza a senha",
    description="Atualiza a senha do usuário alvo.",
)
def update_password(
    target_user_id: int,
    data: UserUpdatePassword,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_password(current_user, data, target_user_id)


@router_user.delete(
    "/delete/{target_user_id}",
    response_model=UserResponse,
    summary="Remove um usuário",
    description="Remove o usuário alvo pelo ID.",
)
def delete_user(
    target_user_id: int = None,
    service: UserService = Depends(get_user_service),
    current_user: UserDB = Depends(get_current_user),
):
    return service.delete_user(current_user, target_user_id)
