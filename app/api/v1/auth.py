import logging

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import AuthService
from app.api.exceps import LoginError
from app.schemas.users import UserCreate, UserResponse , TokenResponse
from app.api.deps import get_db
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.core.rate_limit import limiter
from slowapi.util import get_ipaddr

router_auth = APIRouter(prefix="/auth", tags=["auth"])

logger = logging.getLogger("app.auth")

def get_login_form(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    """Le o formulario de login e guarda o username para a chave do rate limit."""
    request.state.login_username = form_data.username
    return form_data

def _login_key(request: Request) -> str:
    """Chave composta por IP + username: limita brute force sem penalizar o escritorio inteiro."""
    username = getattr(request.state, "login_username", "")
    return f"{get_ipaddr(request)}:{username}"

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
    user: UserDB = Depends(get_current_user)
):

    return service.register_user(data, user)

@router_auth.post(
    "/login",
    response_model=TokenResponse,
    summary="Autenticar usuário",
    description="Autentica um usuário e retorna um token de acesso.",
)
@limiter.limit("5/minute", key_func=_login_key)
def login_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(get_login_form),
    service: AuthService = Depends(get_auth_service),
):
    try:
        return service.authenticate_user(form_data.username, form_data.password)
    except LoginError:

        logger.warning("Login falhou username=%s ip=%s", form_data.username, get_ipaddr(request))
        raise