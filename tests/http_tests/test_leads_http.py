import pytest
from fastapi import status

API_PREFIX = "/api/v1"

def test_create_lead_success(client, auth_headers_owner, http_lead_payload):
    """POST /leads/create deve criar um lead com sucesso."""
    response = client.post(f"{API_PREFIX}/leads/create", json=http_lead_payload, headers=auth_headers_owner)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == http_lead_payload["name"]
    assert data["email"] == http_lead_payload["email"]
    assert data["user_id"] is not None
    assert "id" in data


def test_create_lead_unauthorized(client, http_lead_payload):
    """POST /leads/create sem token retorna 401."""
    response = client.post(f"{API_PREFIX}/leads/create", json=http_lead_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_create_lead_invalid_email(client, auth_headers_owner, http_lead_payload):
    """POST /leads/create com email inválido retorna 422."""
    payload = http_lead_payload.copy()
    payload["email"] = "invalid-email"
    response = client.post(f"{API_PREFIX}/leads/create", json=payload, headers=auth_headers_owner)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_get_all_leads_success(client, auth_headers_owner, owner_leads):
    """GET /leads retorna todos os leads do usuário."""
    response = client.get(f"{API_PREFIX}/leads", headers=auth_headers_owner)
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert all(lead["user_id"] == owner_leads.user_id for lead in data)


def test_get_all_leads_admin(client, auth_headers, owner_leads, foreign_leads):
    """Admin deve ver todos os leads."""
    response = client.get(f"{API_PREFIX}/leads", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 2 


def test_update_lead_success(client, auth_headers_owner, owner_lead, http_lead_update_payload):
    """PATCH /leads/update/{lead_id} atualiza o lead."""
    response = client.patch(
        f"{API_PREFIX}/leads/update/{owner_lead.id}",
        json=http_lead_update_payload,
        headers=auth_headers_owner
    )

    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == http_lead_update_payload["name"]
    assert data["email"] == http_lead_update_payload["email"]
    assert data["status"] == http_lead_update_payload["status"]


def test_update_lead_not_found(client, auth_headers_owner, http_lead_update_payload):
    """PATCH /leads/update/{id} com ID inexistente retorna 404."""
    response = client.patch(f"{API_PREFIX}/leads/update/99999", json=http_lead_update_payload, headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_lead_foreign_user(client, auth_headers_foreign, owner_lead, http_lead_update_payload):
    """Usuário sem permissão não pode atualizar lead de outro."""
    response = client.patch(
        f"{API_PREFIX}/leads/update/{owner_lead.id}",
        json=http_lead_update_payload,
        headers=auth_headers_foreign
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_lead_success(client, auth_headers_owner, owner_lead):
    """DELETE /leads/delete/{lead_id} remove o lead."""
    response = client.delete(f"{API_PREFIX}/leads/delete/{owner_lead.id}", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == owner_lead.id

def test_delete_lead_not_found(client, auth_headers_owner):
    """DELETE /leads/delete/{id} com ID inexistente retorna 404."""
    response = client.delete(f"{API_PREFIX}/leads/delete/99999", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_lead_foreign_user(client, auth_headers_foreign, owner_lead):
    """Usuário sem permissão não pode deletar lead de outro."""
    response = client.delete(f"{API_PREFIX}/leads/delete/{owner_lead.id}", headers=auth_headers_foreign)
    assert response.status_code == status.HTTP_403_FORBIDDEN
