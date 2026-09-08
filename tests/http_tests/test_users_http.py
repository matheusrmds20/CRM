import pytest
from fastapi import status

API_PREFIX = "/api/v1"


def test_update_username_success(client, auth_headers_owner, owner_user, http_user_update_username_payload):
    """PATCH /users/update-username deve atualizar o username."""
    response = client.patch(
        f"{API_PREFIX}/users/update_username/{owner_user.id}",
        json=http_user_update_username_payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == http_user_update_username_payload["username"]


def test_update_username_unauthorized_different_user(client, auth_headers_foreign, owner_user, http_user_update_username_payload):
    """Usuário não pode alterar username de outro usuário."""
    response = client.patch(
        f"{API_PREFIX}/users/update_username/{owner_user.id}",
        json=http_user_update_username_payload,
        headers=auth_headers_foreign
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_update_username_not_found(client, auth_headers_owner, http_user_update_username_payload):
    """PATCH /users/update-username com target_user_id inexistente retorna 404."""
    response = client.patch(
        f"{API_PREFIX}/users/update_username/{99999}",
        json=http_user_update_username_payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_password_success(client, auth_headers_owner, owner_user, http_user_update_password_payload):
    """PATCH /users/update-password deve atualizar a senha."""
    response = client.patch(
        f"{API_PREFIX}/users/update_password/{owner_user.id}",
        json=http_user_update_password_payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == owner_user.id


def test_update_password_wrong_current_password(client, auth_headers_owner, owner_user):
    """PATCH /users/update-password com senha atual incorreta retorna 400."""
    payload = {"current_password": "wrongpass", "new_password": "87654321"}
    response = client.patch(
        f"{API_PREFIX}/users/update_password/{owner_user.id}",
        json=payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_update_password_unauthorized_different_user(client, auth_headers_foreign, owner_user, http_user_update_password_payload):
    """Usuário não pode alterar senha de outro usuário."""
    response = client.patch(
        f"{API_PREFIX}/users/update_password/{owner_user.id}",
        json=http_user_update_password_payload,
        headers=auth_headers_foreign
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN