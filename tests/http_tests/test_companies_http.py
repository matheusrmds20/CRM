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
    payload = {"name": "Falha", "cnpj": "12.345.678/0001-9"}  # inválido
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


def test_get_all_companies_empty(client, auth_headers, empty_companies_db):
    """GET /companies quando não há empresas deve retornar lista vazia ou erro."""
    response = client.get(f"{API_PREFIX}/companies", headers=auth_headers)
    # O service lança ValueError se vazio, então provavelmente 404 ou 400
    assert response.status_code in (status.HTTP_404_NOT_FOUND, status.HTTP_400_BAD_REQUEST)


def test_get_company_by_id_success(client, auth_headers, company):
    """GET /companies/id/{company_id} retorna a empresa correta."""
    response = client.get(f"{API_PREFIX}/companies/id/{company.id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == company.id
    assert data["name"] == company.name


def test_get_company_by_id_not_found(client, auth_headers):
    """GET /companies/id/{id} com ID inexistente retorna 404."""
    response = client.get(f"{API_PREFIX}/companies/id/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_company_by_cnpj_success(client, auth_headers, company):
    """GET /companies/cnpj/{cnpj} retorna a empresa."""

    response = client.get(f"{API_PREFIX}/companies/cnpj", params={"cnpj": company.cnpj}, headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["cnpj"] == company.cnpj


def test_get_company_by_cnpj_not_found(client, auth_headers):
    """GET /companies/cnpj com CNPJ inexistente retorna 404."""
    response = client.get(f"{API_PREFIX}/companies/cnpj", params={"cnpj": "00.000.000/0000-00"}, headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_get_company_by_name_success(client, auth_headers, company):
    """GET /companies/name/{name} retorna a empresa."""
    response = client.get(f"{API_PREFIX}/companies/name/{company.name}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == company.name


def test_get_company_by_name_not_found(client, auth_headers):
    """GET /companies/name/{name} com nome inexistente retorna 404."""
    response = client.get(f"{API_PREFIX}/companies/name/inexistente", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


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

    # Verifica que foi removida
    get_response = client.get(f"{API_PREFIX}/companies/id/{company.id}", headers=auth_headers)
    assert get_response.status_code == status.HTTP_404_NOT_FOUND


def test_delete_company_not_found(client, auth_headers):
    """DELETE /companies/{id} com ID inexistente retorna 404."""
    response = client.delete(f"{API_PREFIX}/companies/delete/99999", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_company_permissions_sales_user(client, auth_headers_sales, http_company_payload):
    """Usuário sales não pode criar empresa (deve retornar 403)."""
    response = client.post(f"{API_PREFIX}/companies/create", json=http_company_payload, headers=auth_headers_sales)
    assert response.status_code == status.HTTP_403_FORBIDDEN

