from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, ItemNotFoundError, NoPermissionError
from app.core.security import hash_password, verify_password



def test_update_username_changes_username(user_service, existing_user, update_username_payload):
    user_context = SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")
    updated = user_service.update_username(user_context, update_username_payload, user_context.id)

    assert updated.username == update_username_payload.username


def test_update_username_raises_when_user_not_found(user_service):
    missing_user = SimpleNamespace(id=999, username="missing")
    payload = SimpleNamespace(username="newusername")

    with pytest.raises(ItemNotFoundError):
        user_service.update_username(missing_user, payload, missing_user.id)


def test_update_username_raises_no_permission_when_ids_do_not_match(user_service, existing_user, another_user, update_username_payload):
    another_user_context = SimpleNamespace(id=another_user.id, username=another_user.username, role="sales")

    with pytest.raises(NoPermissionError):
        user_service.update_username(another_user_context, update_username_payload, target_user_id=existing_user.id)


def test_update_password_changes_password(user_service, existing_user, update_password_payload):
    old_hash = existing_user.hashed_password
    user_context = SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")
    updated = user_service.update_password(user_context, update_password_payload, user_context.id)

    assert updated.hashed_password != old_hash
    assert verify_password(update_password_payload.new_password, updated.hashed_password)


def test_update_password_raises_when_current_password_is_empty(user_service, existing_user):
    payload = SimpleNamespace(current_password="", new_password="87654321")
    user_context = SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")

    with pytest.raises(BadRequestError):
        user_service.update_password(user_context, payload, user_context.id)


def test_update_password_raises_when_current_password_is_wrong(user_service, existing_user):
    payload = SimpleNamespace(current_password="wrongpass", new_password="87654321")
    user_context = SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")

    with pytest.raises(BadRequestError):
        user_service.update_password(user_context, payload, user_context.id)


def test_update_password_raises_no_permission_when_ids_do_not_match(user_service, existing_user, another_user, other_user_in_db, update_password_payload):
    another_user_context = SimpleNamespace(id=another_user.id, username=another_user.username, role="sales")

    with pytest.raises(NoPermissionError):
        user_service.update_password(another_user_context, update_password_payload, target_user_id=existing_user.id)


def test_update_password_raises_when_user_not_found(user_service):
    missing_user = SimpleNamespace(id=999, username="missing", hashed_password=hash_password("12345678"))
    payload = SimpleNamespace(current_password="12345678", new_password="87654321")

    with pytest.raises(ItemNotFoundError):
        user_service.update_password(missing_user, payload, missing_user.id)