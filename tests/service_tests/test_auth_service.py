import pytest
from types import SimpleNamespace
from jose import jwt
from app.api.exceps import ItemAlreadyExistsError, LoginError, BadRequestError
from app.core.config import get_settings
from app.core.security import hash_password
from app.models.users import UserDB
from app.services.auth import AuthService

Settings = get_settings()


# ==================== TESTES DE SUCESSO ====================

def test_register_user_success(db_session, auth_service, auth_payload, admin_user):
    """Deve registrar um novo usuário com sucesso."""
    user = auth_service.register_user(auth_payload)

    assert user.id is not None
    assert user.username == auth_payload.username.lower()
    assert user.role == auth_payload.role
    assert user.is_active is True


def test_register_user_username_lowercase(db_session, auth_service, auth_payload_uppercase, admin_user):
    """Deve converter username para minúsculo ao registrar."""
    user = auth_service.register_user(auth_payload_uppercase)

    assert user.username == "testuser"


def test_authenticate_user_returns_token(db_session, auth_service, auth_payload):
    """Deve retornar um token JWT válido ao autenticar."""
    # Cria usuário diretamente no banco para teste
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()

    result = auth_service.authenticate_user(auth_payload.username, auth_payload.password)

    assert result["token_type"] == "bearer"
    assert isinstance(result["access_token"], str)
    assert result["access_token"] != ""

    # Decodifica e verifica o token
    payload = jwt.decode(
        result["access_token"],
        Settings.SECRET_KEY,
        algorithms=[Settings.ALGORITHM],
    )
    assert payload["sub"] == auth_payload.username


# ==================== TESTES DE ERRO ====================

def test_register_user_already_exists(db_session, auth_service, auth_payload, admin_user):
    """Não deve permitir registrar usuário com username já existente."""
    # Registra o usuário uma vez
    auth_service.register_user(auth_payload)

    # Tenta registrar novamente com o mesmo username
    with pytest.raises(ItemAlreadyExistsError):
        auth_service.register_user(auth_payload)


def test_authenticate_user_not_found(db_session, auth_service):
    """Deve lançar erro ao tentar autenticar usuário inexistente."""
    with pytest.raises(LoginError):
        auth_service.authenticate_user("missing", "12345678")


def test_authenticate_user_wrong_password(db_session, auth_service, auth_payload):
    """Deve lançar erro ao tentar autenticar com senha incorreta."""
    # Cria usuário
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(LoginError):
        auth_service.authenticate_user(auth_payload.username, "wrongpass")


def test_authenticate_user_disabled(db_session, auth_service, auth_payload):
    """Deve lançar erro ao tentar autenticar usuário inativo."""
    # Cria usuário inativo
    user = UserDB(
        username=auth_payload.username,
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_active=False,  # Usuário desativado
    )
    db_session.add(user)
    db_session.commit()

    with pytest.raises(LoginError):
        auth_service.authenticate_user(auth_payload.username, auth_payload.password)


def test_authenticate_user_uppercase_not_found(db_session, auth_service, auth_payload):
    """Deve lançar erro ao tentar autenticar com username em maiúsculo (case-sensitive)."""
    # Cria usuário com username minúsculo
    user = UserDB(
        username=auth_payload.username,  # "testuser"
        hashed_password=hash_password(auth_payload.password),
        role=auth_payload.role,
        is_active=auth_payload.is_active,
    )
    db_session.add(user)
    db_session.commit()

    # Tenta autenticar com username em maiúsculo
    with pytest.raises(LoginError):
        auth_service.authenticate_user("TESTUSER", auth_payload.password)