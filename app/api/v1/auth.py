from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import AuthService
from app.schemas.users import UserCreate, UserResponse , TokenResponse
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.users import UserDB
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.config import get_settings

router_auth = APIRouter(prefix="/auth", tags=["auth"])

limter = Limiter(key_func=get_remote_address)

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)

@router_auth.post(
    "/register",
    response_model=UserResponse,
    summary="Registrar novo usuário",
    description="Cria uma nova conta de usuário no sistema.",
)
def register_user(
    data: UserCreate, 
    service: AuthService = Depends(get_auth_service),
):

    return service.register_user(data)


@router_auth.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Autentica um usuário e retorna um token de acesso.",
)
@limter.limit("5/minute")
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):

    return service.authenticate_user(form_data.username, form_data.password)
