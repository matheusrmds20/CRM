from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, NoPermissionError
from app.core.security import hash_password
from app.models.users import Roles, UserDB
from app.services.users import UserService


@pytest.fixture()
def current_user():
    return SimpleNamespace(id=1, username="testuser")


@pytest.fixture()
def another_user():
    return SimpleNamespace(id=2, username="otheruser")


@pytest.fixture()
def update_username_payload():
    return SimpleNamespace(username="newusername")


@pytest.fixture()
def update_password_payload():
    return SimpleNamespace(current_password="12345678", new_password="87654321")


@pytest.fixture()
def existing_user(db_session):
    user = UserDB(
        username="testuser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_superuser=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def service(db_session):
    return UserService(db_session)


def test_update_username_changes_username(service, db_session, existing_user, current_user, update_username_payload):
    updated = service.update_username(current_user, update_username_payload)

    assert updated.username == update_username_payload.username


def test_update_username_raises_when_username_is_empty(service, current_user):
    payload = SimpleNamespace(username="")

    with pytest.raises(BadRequestError):
        service.update_username(current_user, payload)


def test_update_username_raises_when_user_not_found(service):
    missing_user = SimpleNamespace(id=999, username="missing")
    payload = SimpleNamespace(username="newusername")

    with pytest.raises(BadRequestError):
        service.update_username(missing_user, payload)


def test_update_username_raises_no_permission_when_ids_do_not_match(service, existing_user, another_user, update_username_payload):
    with pytest.raises(NoPermissionError):
        service.update_username(another_user, update_username_payload)


def test_update_password_changes_password(service, db_session, existing_user, current_user, update_password_payload):
    updated = service.update_password(current_user, update_password_payload)

    assert updated.username == existing_user.username
    assert updated.hashed_password != existing_user.hashed_password


def test_update_password_raises_when_current_password_is_empty(service, current_user):
    payload = SimpleNamespace(current_password="", new_password="87654321")

    with pytest.raises(BadRequestError):
        service.update_password(current_user, payload)


def test_update_password_raises_when_new_password_is_empty(service, current_user):
    payload = SimpleNamespace(current_password="12345678", new_password="")

    with pytest.raises(BadRequestError):
        service.update_password(current_user, payload)


def test_update_password_raises_when_current_password_is_wrong(service, existing_user, current_user):
    payload = SimpleNamespace(current_password="wrongpass", new_password="87654321")

    with pytest.raises(BadRequestError):
        service.update_password(current_user, payload)


def test_update_password_raises_when_user_not_found(service):
    missing_user = SimpleNamespace(id=999, username="missing", hashed_password=hash_password("12345678"))
    payload = SimpleNamespace(current_password="12345678", new_password="87654321")

    with pytest.raises(BadRequestError):
        service.update_password(missing_user, payload)


def test_update_password_raises_no_permission_when_ids_do_not_match(service, existing_user, another_user, update_password_payload):
    with pytest.raises(NoPermissionError):
        service.update_password(another_user, update_password_payload)
