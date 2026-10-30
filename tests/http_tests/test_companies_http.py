import pytest
from fastapi import status
from urllib.parse import quote

API_PREFIX = "/api/v1"

def test_create_company_success(client, auth_headers, http_company_payload):
    """POST /companies/create deve criar uma empresa com sucesso."""

    response = client.post(f"{API_PREFIX}/companies/create", json=http_company_payload, headers=auth_headers)

    print(response.json())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == http_company_payload["name"]
    assert data["cnpj"] == http_company_payload["cnpj"]
    assert "id" in data

def test_create_company_unauthorized_without_token(client, http_company_payload):
    """POST /companies/create sem token deve retornar 401."""
    response = client.post(f"{API_PREFIX}/companies/create", json=http_company_payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_create_company_invalid_cnpj(client, auth_headers):
    """POST /companies/create com CNPJ inválido deve retornar 422."""
    payload = {"name": "Falha", "cnpj": "12.345.678/0001-9"}
    response = client.post(f"{API_PREFIX}/companies/create", json=payload, headers=auth_headers)
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

def test_get_all_companies_success(client, auth_headers, company):
    """GET /companies deve listar todas as empresas."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(c["id"] == company.id for c in data)

def test_update_company_with_null_cnpj_keeps_value(client, auth_headers, company):
    """PATCH com cnpj: null deve manter o valor atual (nunca 500)."""
    response = client.patch(
        f"{API_PREFIX}/companies/update/{company.id}",
        json={"name": "Nome Atualizado", "cnpj": None},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cnpj"] == company.cnpj

def test_get_all_companies_empty(client, auth_headers, empty_companies_db):
    """GET /companies sem empresas deve retornar uma lista vazia."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == []

def test_update_company_success(client, auth_headers, company, http_company_update_payload):
    """PATCH /companies/{company_id} atualiza a empresa."""
    response = client.patch(
        f"{API_PREFIX}/companies/update/{company.id}",
        json=http_company_update_payload,
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == http_company_update_payload["name"]
    assert data["cnpj"] == http_company_update_payload["cnpj"]

def test_update_company_not_found(client, auth_headers, http_company_update_payload):
    """PATCH /companies/{id} com ID inexistente retorna 404."""
    response = client.patch(f"{API_PREFIX}/companies/update/99999", json=http_company_update_payload, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_company_success(client, auth_headers, company):
    """DELETE /companies/{company_id} remove a empresa."""
    response = client.delete(f"{API_PREFIX}/companies/delete/{company.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == company.id

def test_delete_company_not_found(client, auth_headers):
    """DELETE /companies/{id} com ID inexistente retorna 404."""
    response = client.delete(f"{API_PREFIX}/companies/delete/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_company_with_leads_blocked(client, auth_headers, company, owner_lead):
    """DELETE /companies/{id} com leads vinculados retorna 400 com mensagem clara."""
    response = client.delete(f"{API_PREFIX}/companies/delete/{company.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "Existem leads vinculados" in response.json()["detail"]

def test_deactivate_company_removes_from_listing(client, auth_headers, company):
    """PATCH com is_active: false remove a empresa da listagem."""
    response = client.patch(
        f"{API_PREFIX}/companies/update/{company.id}",
        json={"is_active": False},
        headers=auth_headers,
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["is_active"] is False

    listing = client.get(f"{API_PREFIX}/companies", headers=auth_headers)
    assert all(c["id"] != company.id for c in listing.json())

def test_company_response_exposes_is_active(client, auth_headers, company):
    """CompanyResponse expõe o campo is_active."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers)
    data = response.json()
    match = next((c for c in data if c["id"] == company.id), None)
    assert match is not None
    assert "is_active" in match

def test_company_permissions_sales_user(client, auth_headers_sales, http_company_payload):
    """Usuário sales não pode criar empresa (deve retornar 403)."""
    response = client.post(f"{API_PREFIX}/companies/create", json=http_company_payload, headers=auth_headers_sales)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_all_companies_allowed_for_sales_user(client, auth_headers_sales, company):
    """Usuário sales pode listar empresas (leitura liberada para todos os perfis)."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers_sales)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert any(c["id"] == company.id for c in data)

def test_update_company_forbidden_for_sales_user(client, auth_headers_sales, company, http_company_update_payload):
    """Usuário sales não pode atualizar empresa."""
    response = client.patch(
        f"{API_PREFIX}/companies/update/{company.id}",
        json=http_company_update_payload,
        headers=auth_headers_sales,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_company_forbidden_for_sales_user(client, auth_headers_sales, company):
    """Usuário sales não pode deletar empresa."""
    response = client.delete(f"{API_PREFIX}/companies/delete/{company.id}", headers=auth_headers_sales)
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_all_companies_allowed_for_manager_user(client, auth_headers_manager, company):
    """Usuário manager pode listar empresas."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers_manager)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)