from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth import AuthService
from app.schemas.users import UserCreate, UserResponse , TokenResponse
from app.api.deps import get_db
from sqlalchemy.orm import Session


router_auth = APIRouter(prefix="/auth", tags=["auth"])


@router_auth.post("/register", response_model=UserResponse)
def register_user(
    data: UserCreate, 
    db: Session = Depends(get_db)
):
    service = AuthService(db)

    return service.register_user(data)


@router_auth.post("/login", response_model=TokenResponse)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    service = AuthService(db)

    return service.authenticate_user(form_data)
