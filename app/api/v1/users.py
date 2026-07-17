from fastapi import APIRouter, Depends
from app.services.users import UserService
from app.schemas.users import UserResponse, UserUpdateUsername, UserUpdatePassword
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_user = APIRouter(prefix="/users", tags=["users"])


@router_user.patch("/update-username", response_model=UserResponse)
def update_username(
    data: UserUpdateUsername,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = UserService(db)

    return service.update_username(current_user, data)


@router_user.patch("/update-password", response_model=UserResponse)
def update_password(
    data: UserUpdatePassword,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = UserService(db)

    return service.update_password(current_user, data)
