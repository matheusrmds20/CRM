import pytest
from fastapi import status

API_PREFIX = "/api/v1"

def test_create_proposal_success(client, auth_headers_owner, http_proposal_payload):
    """POST /proposals/create deve criar uma proposta com sucesso."""
    response = client.post(f"{API_PREFIX}/proposals/create", json=http_proposal_payload, headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["lead_id"] == http_proposal_payload["lead_id"]
    assert data["user_id"] is not None
    assert data["value"] == http_proposal_payload["value"]
    assert "id" in data




def test_create_proposal_foreign_lead(client, auth_headers_owner, foreign_lead):
    """Usuário não pode criar proposta para lead de outro."""
    payload = {"lead_id": foreign_lead.id, "status": "pending", "value": 150.0, "sent_at": None}
    response = client.post(f"{API_PREFIX}/proposals/create", json=payload, headers=auth_headers_owner)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_proposal_by_lead_id_success(client, auth_headers_owner, owner_proposals):
    """GET /proposals/lead_id/{lead_id} retorna a proposta do lead."""
    lead_id = owner_proposals.lead_id
    response = client.get(f"{API_PREFIX}/proposals/lead_id/{lead_id}", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["lead_id"] == lead_id


def test_update_proposal_success(client, auth_headers_owner, owner_proposals, http_proposal_update_payload):
    """PATCH /proposals/{proposal_id} atualiza a proposta."""
    proposal_id = owner_proposals.id
    response = client.patch(
        f"{API_PREFIX}/proposals/update/{proposal_id}",
        json=http_proposal_update_payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == http_proposal_update_payload["status"]
    assert data["value"] == http_proposal_update_payload["value"]


def test_update_proposal_not_found(client, auth_headers_owner, http_proposal_update_payload):
    """PATCH /proposals/{id} com ID inexistente retorna 404."""
    response = client.patch(f"{API_PREFIX}proposals/update/99999", json=http_proposal_update_payload, headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_update_proposal_foreign_user(client, auth_headers_foreign, owner_proposals, http_proposal_update_payload):
    """Usuário sem permissão não pode atualizar proposta de outro."""
    proposal_id = owner_proposals.id
    response = client.patch(
        f"{API_PREFIX}/proposals/update/{proposal_id}",
        json=http_proposal_update_payload,
        headers=auth_headers_foreign
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_proposal_success(client, auth_headers_owner, owner_proposals):
    """DELETE /proposals/{proposal_id} remove a proposta."""
    proposal_id = owner_proposals.id
    response = client.delete(f"{API_PREFIX}/proposals/delete/{proposal_id}", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == proposal_id

def test_delete_proposal_not_found(client, auth_headers_owner):
    """DELETE /proposals/{id} com ID inexistente retorna 404."""
    response = client.delete(f"{API_PREFIX}/proposals/99999", headers=auth_headers_owner)
    assert response.status_code == status.HTTP_404_NOT_FOUND
