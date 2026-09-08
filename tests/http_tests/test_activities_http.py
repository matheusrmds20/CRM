import pytest
from fastapi import status

API_PREFIX = "/api/v1"


def test_create_activity_success(client, auth_headers_owner, http_activity_payload):
    response = client.post(
        f"{API_PREFIX}/activities/create", 
        json=http_activity_payload, 
        headers=auth_headers_owner
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json() if response.status_code != 200 else 'OK'}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["lead_id"] == http_activity_payload["lead_id"]
    assert data["user_id"] is not None
    assert data["description"] == http_activity_payload["description"]
    assert "id" in data




def test_get_activity_by_id_success(client, auth_headers_owner, owner_activities):
    activity_id = owner_activities.id
    response = client.get(
        f"{API_PREFIX}/activities/id/{activity_id}", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == activity_id



def test_get_activity_by_lead_id_success(client, auth_headers_owner, owner_activities):
    lead_id = owner_activities.lead_id
    response = client.get(
        f"{API_PREFIX}/activities/lead_id/{lead_id}", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert all(a["lead_id"] == lead_id for a in data)


def test_get_activity_by_user_id_success(client, auth_headers_owner, owner_activities):
    user_id = owner_activities.user_id
    response = client.get(
        f"{API_PREFIX}/activities/user_id/{user_id}", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert all(a["user_id"] == user_id for a in data)


def test_update_activity_success(client, auth_headers_owner, owner_activities, http_activity_update_payload):
    activity_id = owner_activities.id
    response = client.patch(
        f"{API_PREFIX}/activities/update/{activity_id}",
        json=http_activity_update_payload,
        headers=auth_headers_owner,
    )

    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["description"] == http_activity_update_payload["description"]
    assert data["activity_type"] == http_activity_update_payload["activity_type"]





def test_update_activity_foreign_user(client, auth_headers_owner, foreign_activity, http_activity_update_payload):
    activity_id = foreign_activity.id
    response = client.patch(
        f"{API_PREFIX}/activities/update/{activity_id}",
        json=http_activity_update_payload,
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_delete_activity_success(client, auth_headers_owner, owner_activities):
    """DELETE /activities/{activity_id} remove a atividade."""
    activity_id = owner_activities.id
    response = client.delete(
        f"{API_PREFIX}/activities/delete/{activity_id}", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == activity_id



    get_response = client.get(
        f"{API_PREFIX}/activities/id/{activity_id}", 
        headers=auth_headers_owner
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND



# Erros -------------------------------------------------------------------------------------------


def test_create_activity_error(client, auth_headers_owner, http_activity_payload):
    payload = {"lead_id": http_activity_payload["lead_id"], "description": "", "activity_type": "call", "done_at": None}

    response = client.post(
        f"{API_PREFIX}/activities/create", 
        json=payload,
        headers=auth_headers_owner
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_create_activity_foreign_lead(client, auth_headers_owner, foreign_lead):

    payload = {"lead_id": foreign_lead.id, "description": "Teste", "activity_type": "call", "done_at": None}
    response = client.post(
        f"{API_PREFIX}/activities/create", 
        json=payload, headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_get_activity_by_id_not_found(client, auth_headers_owner):
    response = client.get(
        f"{API_PREFIX}/activities/id/99999", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND


    
def test_update_activity_not_found(client, auth_headers_owner, http_activity_update_payload):
    response = client.patch(
        f"{API_PREFIX}/activities/update/99999", 
        json=http_activity_update_payload, 
        headers=auth_headers_owner
    )

    
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_activity_not_found(client, auth_headers_owner):
    response = client.delete(
        f"{API_PREFIX}/activities/delete/99999", 
        headers=auth_headers_owner
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND