import pytest
from app.api.exceps import ItemNotFoundError, NoPermissionError, ItemAlreadyExistsError
from app.models.leads import StatusLeads

def test_create_lead_success(leads_service, owner_context, lead_payload):
    result = leads_service.create_lead(owner_context, lead_payload)

    assert result.id is not None
    assert result.user_id == owner_context.id
    assert result.email == lead_payload.email
    assert result.name == lead_payload.name.lower()

def test_create_lead_raises_when_company_not_found(leads_service, owner_context, company):
    """Criar lead com empresa inexistente deve falhar com ItemNotFoundError."""
    from app.schemas.leads import LeadCreate
    payload = LeadCreate(
        name="Orphan Lead",
        email="orphan@example.com",
        phone="11999999999",
        company_id=99999,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        status=StatusLeads.NEW,
    )

    with pytest.raises(ItemNotFoundError, match="Empresa nao encontrada"):
        leads_service.create_lead(owner_context, payload)

def test_create_lead_allows_null_company(leads_service, owner_context):
    """Lead sem empresa (company_id nulo) e permitido."""
    from app.schemas.leads import LeadCreate
    payload = LeadCreate(
        name="No Company",
        email="nocompany@example.com",
        phone="11999999999",
        company_id=None,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        status=StatusLeads.NEW,
    )

    result = leads_service.create_lead(owner_context, payload)
    assert result.id is not None
    assert result.company_id is None

def test_create_lead_raises_when_email_already_exists(leads_service, owner_context, lead_create_with_existing_email, lead):
    with pytest.raises(ItemAlreadyExistsError):
        leads_service.create_lead(owner_context, lead_create_with_existing_email)

def test_list_leads_success(leads_service, owner_context, owner_lead):
    result = leads_service.get_all_leads(owner_context)
    assert len(result) == 1
    assert result[0].id == owner_lead.id

def test_list_leads_returns_empty_list_when_empty(leads_service, owner_context, empty_leads_db):
    assert leads_service.get_all_leads(owner_context) == []

def test_list_leads_sales_user_only_sees_own_records(leads_service, owner_context, owner_leads, foreign_leads):
    result = leads_service.get_all_leads(owner_context)

    assert len(result) == 1
    assert all(lead.user_id == owner_context.id for lead in result)

def test_list_leads_admin_can_access(leads_service, admin_context, owner_leads, foreign_leads):
    result = leads_service.get_all_leads(admin_context)
    assert len(result) == 2

def test_list_leads_manager_can_access(leads_service, manager_context, owner_leads, foreign_leads):
    result = leads_service.get_all_leads(manager_context)
    assert len(result) == 2

def test_update_lead_success(leads_service, owner_context, owner_lead, lead_update_payload):
    result = leads_service.update_lead(owner_lead.id, owner_context, lead_update_payload)

    assert result.id == owner_lead.id
    assert result.name == "Lead Updated"
    assert result.email == "updated@example.com"
    assert result.status == StatusLeads.CONTACTED
    assert result.is_active is False

def test_update_lead_raises_when_company_not_found(leads_service, owner_context, owner_lead):
    """Atualizar o company_id do lead para uma empresa inexistente deve falhar."""
    from app.schemas.leads import LeadUpdate
    payload = LeadUpdate(company_id=99999)

    with pytest.raises(ItemNotFoundError, match="Empresa nao encontrada"):
        leads_service.update_lead(owner_lead.id, owner_context, payload)

def test_update_lead_raises_when_not_found(leads_service, owner_context, lead_update_missing_payload):
    with pytest.raises(ItemNotFoundError, match="Nenhum lead encontrado"):
        leads_service.update_lead(9999, owner_context, lead_update_missing_payload)

def test_update_lead_raises_no_permission(leads_service, foreign_context, owner_lead, lead_update_foreign_payload):
    with pytest.raises(NoPermissionError):
        leads_service.update_lead(owner_lead.id, foreign_context, lead_update_foreign_payload)

def test_delete_lead_success(leads_service, owner_context, owner_lead):
    result = leads_service.delete_lead(owner_lead.id, owner_context)

    assert result.id == owner_lead.id

def test_delete_lead_raises_when_not_found(leads_service, owner_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum lead encontrado"):
        leads_service.delete_lead(9999, owner_context)

def test_delete_lead_raises_no_permission(leads_service, foreign_context, owner_lead):
    with pytest.raises(NoPermissionError):
        leads_service.delete_lead(owner_lead.id, foreign_context)