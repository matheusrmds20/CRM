import pytest
from app.api.exceps import ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError, BadRequestError
from types import SimpleNamespace
from app.schemas.activities import ActivityCreate
from app.models.activities import ActivityType

def test_create_activity_success(activity_service, owner_context, activity_payload):
    result = activity_service.create_activity(owner_context, activity_payload)
    assert result.id is not None
    assert result.lead_id == activity_payload.lead_id
    assert result.user_id == owner_context.id
    assert result.activity_type == activity_payload.activity_type
    assert result.description == activity_payload.description

def test_create_activity_raises_item_not_found_when_lead_missing(activity_service, owner_context):
    payload = ActivityCreate(lead_id=9999, description="Ligacao de acompanhamento", activity_type=ActivityType.CALL, done_at=None)
    with pytest.raises(ItemNotFoundError, match="Nenhum lead encontrado"):
        activity_service.create_activity(owner_context, payload)

def test_create_activity_raises_no_permission_for_foreign_lead(activity_service, owner_context, foreign_lead):
    payload = ActivityCreate(lead_id=foreign_lead.id, description="Ligacao de acompanhamento", activity_type=ActivityType.CALL, done_at=None)
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        activity_service.create_activity(owner_context, payload)

def test_get_activity_by_lead_id_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context, activity_payload)
    result = activity_service.get_activity_by_lead_id(owner_context, activity.lead_id)
    assert len(result) == 1
    assert result[0].id == activity.id
    assert result[0].lead_id == activity.lead_id

def test_get_activity_by_lead_id_raises_when_lead_not_found(activity_service, owner_context):
    """Lead inexistente nao retorna lista vazia: e 404."""
    with pytest.raises(ItemNotFoundError, match="Nenhum lead encontrado"):
        activity_service.get_activity_by_lead_id(owner_context, 9999)

def test_get_activity_by_lead_id_raises_no_permission_for_foreign_lead_without_activities(activity_service, owner_context, foreign_lead):
    """Lead alheio sem atividades: a checagem e sobre o lead, nao sobre a lista (403, nao 200 vazio)."""
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        activity_service.get_activity_by_lead_id(owner_context, foreign_lead.id)

def test_get_activity_by_lead_id_manager_can_view_foreign_lead_activities(activity_service, manager_context, owner_context, owner_lead, activity_payload):
    activity = activity_service.create_activity(owner_context, activity_payload)
    result = activity_service.get_activity_by_lead_id(manager_context, activity.lead_id)
    assert len(result) == 1
    assert result[0].id == activity.id

def test_update_activity_success(activity_service, owner_context, activity_payload, activity_update_payload):
    activity = activity_service.create_activity(owner_context, activity_payload)
    result = activity_service.update_activity(activity.id, owner_context, activity_update_payload)
    assert result.id == activity.id
    assert result.description == "Ligacao atualizada"
    assert result.activity_type == ActivityType.EMAIL

def test_update_activity_raises_item_not_found(activity_service, owner_context, activity_update_payload):
    with pytest.raises(ItemNotFoundError, match="Nenhum activity encontrado"):
        activity_service.update_activity(9999, owner_context, activity_update_payload)

def test_update_activity_raises_no_permission_when_foreign_user(activity_service, owner_context, foreign_activity, activity_update_payload):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        activity_service.update_activity(foreign_activity.id, owner_context, activity_update_payload)

def test_delete_activity_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context, activity_payload)
    result = activity_service.delete_activity(activity.id, owner_context)
    assert result.id == activity.id

def test_delete_activity_raises_item_not_found(activity_service, owner_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum activity encontrado"):
        activity_service.delete_activity(9999, owner_context)

def test_delete_activity_raises_no_permission_when_foreign_user(activity_service, owner_context, foreign_activity):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        activity_service.delete_activity(foreign_activity.id, owner_context)