"""Testes de integridade referencial contra banco com FK de fato habilitada.

Estes testes rodam contra o PostgreSQL real (CI) ou, localmente, contra o SQLite
em memória com ``PRAGMA foreign_keys=ON``. A ideia é garantir que o que o SQLite
silenciosamente ignorava (video aqui: item P2-19/20/21 quebrar em produção) seja
coberto por uma suíte que falha se o banco não respeitar as FK.

Padrão: marcados como ``integration`` para que a equipe possa executá-los somente
onde a infraestrutura de banco existir (CI/Postgres).
"""

import pytest
from sqlalchemy.exc import IntegrityError

from app.models.leads import LeadsDB, StatusLeads
from app.models.users import UserDB

pytestmark = pytest.mark.integration

def test_lead_com_company_inexistente_levantado_no_service(leads_service, owner_context, db_session, owner_user):
    """Criar lead apontando para company inexistente nao deve inserir nem quebrar o banco.

    A validacao de existencia da empresa acontece no service (item 19 do plano) e
    deve retornar 404 — antes de qualquer tentativa de INSERT com FK invalida.
    """
    from app.api.exceps import ItemNotFoundError
    from app.schemas.leads import LeadCreate

    payload = LeadCreate(
        name="Lead Sem Empresa",
        email="sem-empresa@example.com",
        phone="11911111111",
        company_id=999999,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        status=StatusLeads.NEW,
    )

    with pytest.raises(ItemNotFoundError, match="Empresa nao encontrada"):
        leads_service.create_lead(owner_context, payload)

    count = db_session.query(LeadsDB).count()
    assert count == 0

def test_db_rejeita_fk_invalida_direto_no_insert(db_session, owner_user):
    """O banco em si deve rejeitar um lead com company_id que nao existe.

    Este é o teste que FALHA se as FK nao forem respeitadas (SQLite sem
    ``PRAGMA foreign_keys`` ou um schema sem contraint). Em banco correto,
    o INSERT levanta IntegrityError.
    """
    lead = LeadsDB(
        name="Lead FK",
        email="fk-invalida@example.com",
        phone="11922222222",
        user_id=owner_user.id,
        company_id=999999,
        status=StatusLeads.NEW,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        is_active=True,
    )
    db_session.add(lead)

    with pytest.raises(IntegrityError):
        db_session.commit()

    db_session.rollback()

def test_delete_company_com_leads_levantado_no_service(company_service, owner_lead, admin_context, owner_user):
    """Excluir empresa que ainda possui leads nao deve apagá-los em cascata (item 20)."""
    from app.api.exceps import BadRequestError

    company_id = owner_lead.company_id
    assert company_id is not None

    with pytest.raises(BadRequestError, match="Existem leads vinculados a esta empresa"):
        company_service.delete_company(admin_context, company_id)

def test_soft_delete_usuario_preserva_os_leads(db_session, user_service, admin_context, owner_user, owner_lead):
    """Excluir usuario usa soft delete e preserva leads vinculados (item 11)."""

    assert admin_context.id != owner_user.id

    user_service.delete_user(admin_context, owner_user.id)

    lead = db_session.query(LeadsDB).filter(LeadsDB.id == owner_lead.id).one()
    assert lead.user_id == owner_user.id

    user = db_session.query(UserDB).filter(UserDB.id == owner_user.id).one()
    assert user.is_active is False