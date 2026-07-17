from types import SimpleNamespace

import pytest
from jose import jwt

from app.api.exceps import BadRequestError, ItemAlreadyExistsError, LoginError, NoPermissionError, UnauthorizedError, ItemNotFoundError
from app.core.config import settings
from app.core.security import hash_password
from app.models.users import Roles, UserDB
from app.services.auth import AuthService


@pytest.fixture()
def auth_payload():
    return SimpleNamespace(
        username="testuser",
        password="12345678",
        role=Roles.SALES,
        is_superuser=False,
        is_active=True,
        name="Test User",
    )


@pytest.fixture()
def auth_form_data():
    return SimpleNamespace(username="testuser", password="12345678")


@pytest.fixture()
def auth_payload_uppercase():
    return SimpleNamespace(
        username="TESTUSER",
        password="12345678",
        role=Roles.SALES,
        is_superuser=False,
        is_active=True,
        name="Test User",
    )





# TESTES DE EXITO






def test_register_user_Criar_usuario(db_session, auth_payload):
    service = AuthService(db_session)

    user = service.register_user(auth_payload)

    assert user.id is not None
    assert user.username == auth_payload.username.lower()
    assert user.role == auth_payload.role
    assert user.is_superuser is False
    assert user.is_active is True


def test_register_user_Username_minusculo(db_session, auth_payload_uppercase):
    service = AuthService(db_session)

    user = service.register_user(auth_payload_uppercase)

    assert user.username == "testuser"




def test_authenticate_user_Retorna_token(db_session, auth_payload, auth_form_data):
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_superuser=auth_payload.is_superuser,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = AuthService(db_session)

    result = service.authenticate_user(auth_form_data)

    assert result["token_type"] == "bearer"
    assert isinstance(result["access_token"], str)
    assert result["access_token"] != ""

    payload = jwt.decode(
        result["access_token"],
        settings.SECRET_KEY,
        algorithms=[settings.ALGORITHM],
    )
    assert payload["sub"] == auth_payload.username





# TESTES DE ERROS





def test_register_user_Ja_existe(db_session, auth_payload):
    service = AuthService(db_session)
    service.register_user(auth_payload)

    with pytest.raises(ItemAlreadyExistsError):
        service.register_user(auth_payload)


def test_authenticate_user_Usuario_nao_encontrado(db_session):
    service = AuthService(db_session)
    form_data = SimpleNamespace(username="missing", password="12345678")

    with pytest.raises(ItemNotFoundError):
        service.authenticate_user(form_data)


def test_authenticate_user_Senha_incorreta(db_session, auth_payload):
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_superuser=auth_payload.is_superuser,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = AuthService(db_session)
    form_data = SimpleNamespace(username=auth_payload.username, password="wrongpass")

    with pytest.raises(LoginError):
        service.authenticate_user(form_data)


def test_authenticate_user_Usuario_desativado(db_session, auth_payload):
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_superuser=auth_payload.is_superuser,
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = AuthService(db_session)
    form_data = SimpleNamespace(username=auth_payload.username, password=auth_payload.password)

    with pytest.raises(LoginError):
        service.authenticate_user(form_data)



def test_authenticate_user_Usuario_maiusculo_nao_encontrado(db_session, auth_payload):
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_superuser=auth_payload.is_superuser,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    service = AuthService(db_session)
    form_data = SimpleNamespace(username="TESTUSER", password=auth_payload.password)

    with pytest.raises(ItemNotFoundError):
        service.authenticate_user(form_data)
