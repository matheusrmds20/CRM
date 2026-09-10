import pytest
from app.api.exceps import ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError



def test_create_company_success_for_admin(company_service, admin_context, company_payload):
    result = company_service.create_company(admin_context, company_payload)

    assert result.id is not None
    assert result.name == company_payload.name.lower()
    assert result.cnpj == company_payload.cnpj


def test_create_company_success_for_manager(company_service, admin_context, company_payload):
    result = company_service.create_company(admin_context, company_payload)

    assert result.id is not None
    assert result.name == company_payload.name.lower()


def test_create_company_raises_unauthorized_for_sales_user(company_service, sales_context, company_payload):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        company_service.create_company(sales_context, company_payload)


def test_create_company_raises_when_cnpj_already_exists(company_service, admin_context, duplicate_company_payload, company):
    with pytest.raises(ItemAlreadyExistsError, match="Company"):
        company_service.create_company(admin_context, duplicate_company_payload)


# Get

# List

def test_get_all_companies_success(company_service, admin_context, all_companies):
    result = company_service.get_all_companies(admin_context)

    assert len(result) == 2
    assert [item.id for item in result] == [company.id for company in all_companies]


def test_get_all_companies_returns_empty_list_when_empty(company_service, admin_context, empty_companies_db):
    assert company_service.get_all_companies(admin_context) == []


def test_get_all_companies_raises_unauthorized_for_sales_user(company_service, sales_context, all_companies):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        company_service.get_all_companies(sales_context)


# Update

def test_update_company_success(company_service, admin_context, company, company_update_payload):
    result = company_service.update_company(admin_context, company.id, company_update_payload)

    assert result.id == company.id
    assert result.name == company_update_payload.name
    assert result.cnpj == company_update_payload.cnpj


def test_update_company_success_with_partial_payload(company_service, admin_context, company, company_name_update_payload):
    result = company_service.update_company(admin_context, company.id, company_name_update_payload)

    assert result.id == company.id
    assert result.name == company_name_update_payload.name
    assert result.cnpj == company.cnpj


def test_update_company_raises_when_not_found(company_service, admin_context, company_update_payload):
    with pytest.raises(ItemNotFoundError, match="Nenhum company encontrado"):
        company_service.update_company(admin_context, 9999, company_update_payload)


def test_update_company_raises_unauthorized_for_sales_user(company_service, sales_context, company, company_update_payload):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        company_service.update_company(sales_context, company.id, company_update_payload)


# Delete

def test_delete_company_success_for_admin(company_service, admin_context, company):
    result = company_service.delete_company(admin_context, company.id)

    assert result.id == company.id


def test_delete_company_success_for_manager(company_service, admin_context, company):
    result = company_service.delete_company(admin_context, company.id)

    assert result.id == company.id


def test_delete_company_raises_unauthorized_for_sales_user(company_service, sales_context, company):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        company_service.delete_company(sales_context, company.id)


def test_delete_company_raises_when_not_found(company_service, admin_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum company encontrado"):
        company_service.delete_company(admin_context, 9999)
