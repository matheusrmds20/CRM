from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, ItemNotFoundError, NoPermissionError, ItemAlreadyExistsError
from app.core.security import hash_password, verify_password
from app.models.leads import LeadsDB

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

def test_update_username_raises_when_username_already_taken(user_service, existing_user, other_user_in_db):
    """Renomear para um username que ja pertence a outro usuario retorna ItemAlreadyExistsError."""
    user_context = SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")
    payload = SimpleNamespace(username=other_user_in_db.username)

    with pytest.raises(ItemAlreadyExistsError):
        user_service.update_username(user_context, payload, target_user_id=existing_user.id)

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

def test_get_user_by_id_raises_when_user_not_found(user_service):
    """Usuario inexistente retorna ItemNotFoundError, nao estoura erro interno."""
    missing_user = SimpleNamespace(id=999, role="admin")

    with pytest.raises(ItemNotFoundError):
        user_service.get_user_by_id(missing_user, 999)

def test_update_user_blocks_self_role_demotion(user_service, admin_user):
    """Admin nao pode rebaixar o proprio perfil."""
    admin_context = SimpleNamespace(id=admin_user.id, username=admin_user.username, role="admin")
    payload = SimpleNamespace(username=admin_user.username, role="sales")

    with pytest.raises(BadRequestError, match="Não é possível alterar o próprio perfil"):
        user_service.update_user(admin_context, payload, target_user_id=admin_user.id)

def test_update_user_blocks_demoting_last_admin(user_service, db_session, admin_user):
    """Rebaixar o ultimo admin deixa o sistema sem administrador: e bloqueado."""

    admin_context = SimpleNamespace(id=9999, username="other_admin", role="admin")
    payload = SimpleNamespace(username=admin_user.username, role="sales")

    with pytest.raises(BadRequestError, match="pelo menos um administrador ativo"):
        user_service.update_user(admin_context, payload, target_user_id=admin_user.id)

def test_update_user_demotes_admin_when_other_admin_exists(user_service, db_session, admin_user):
    """Com dois admins ativos, rebaixar um deles e permitido."""
    from app.models.users import UserDB
    from app.core.security import hash_password as _hp

    second_admin = UserDB(username="secondadmin", hashed_password=_hp("12345678"), role="admin", is_active=True)
    db_session.add(second_admin)
    db_session.commit()
    db_session.refresh(second_admin)

    admin_context = SimpleNamespace(id=admin_user.id, username=admin_user.username, role="admin")
    payload = SimpleNamespace(username="secondadmin", role="sales")

    updated = user_service.update_user(admin_context, payload, target_user_id=second_admin.id)
    assert updated.role == "sales"

def test_delete_user_blocks_self_exclusion(user_service, admin_user):
    """Admin nao pode se auto-excluir."""
    admin_context = SimpleNamespace(id=admin_user.id, username=admin_user.username, role="admin")

    with pytest.raises(BadRequestError, match="Não é possível excluir o próprio usuário"):
        user_service.delete_user(admin_context, target_user_id=admin_user.id)

def test_delete_user_soft_deletes_preserving_leads(user_service, db_session, admin_user, owner_user, owner_lead, manager_user):
    """Excluir um usuario nao apaga os leads dele: o usuario fica inativo."""
    admin_context = SimpleNamespace(id=admin_user.id, username=admin_user.username, role="admin")

    deleted = user_service.delete_user(admin_context, target_user_id=owner_user.id)

    assert deleted.is_active is False
    assert deleted.id == owner_user.id

    assert user_service.repository.get_user_by_id(owner_user.id) is not None
    leads = db_session.query(LeadsDB).all()
    assert any(lead.id == owner_lead.id for lead in leads)

def test_delete_user_blocks_deleting_last_admin(user_service, admin_user):
    """Excluir o ultimo admin deixa o sistema sem administrador: e bloqueado."""

    admin_context = SimpleNamespace(id=9999, username="other_admin", role="admin")

    with pytest.raises(BadRequestError, match="pelo menos um administrador ativo"):
        user_service.delete_user(admin_context, target_user_id=admin_user.id)