import os
import sys
from pathlib import Path
from types import SimpleNamespace

os.environ['DEBUG'] = 'false'

os.environ.setdefault('SECRET_KEY', 'chave-apenas-para-testes-0123456789abcdef')

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient

import app.models.activities
import app.models.companies
import app.models.leads
import app.models.proposals
import app.models.users
from app.api.deps import get_db
from app.core.security import hash_password
from app.db.base import Base
from app.main import app
from app.models.activities import ActivityDB, ActivityType
from app.models.companies import CompanyDB
from app.models.leads import LeadsDB, StatusLeads
from app.models.proposals import ProposalDB
from app.models.proposals import StatusProposal as StatusProposalDB
from app.models.users import Roles, UserDB
from app.schemas.activities import ActivityCreate, ActivityUpdate
from app.schemas.companies import CompanyCreate, CompanyUpdate
from app.schemas.leads import LeadCreate, LeadUpdate
from app.schemas.proposals import ProposalCreate, ProposalUpdate
from app.services.activities import ActivityService
from app.services.auth import AuthService
from app.services.companies import CompanyService
from app.services.leads import LeadsService
from app.services.proposals import ProposalService
from app.services.users import UserService

TEST_DATABASE_URL = os.environ.get('TEST_DATABASE_URL', 'sqlite://')

_is_postgres = TEST_DATABASE_URL.startswith('postgres')

if _is_postgres:

    engine = create_engine(TEST_DATABASE_URL)
else:
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, 'connect')
    def _ativa_fk_sqlite(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope='session', autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    try:
        yield session
    finally:
        session.close()

        if transaction.is_active:
            transaction.rollback()
        connection.close()

@pytest.fixture()
def company_service(db_session):
    return CompanyService(db_session)

@pytest.fixture()
def leads_service(db_session):
    return LeadsService(db_session)

@pytest.fixture()
def proposal_service(db_session):
    return ProposalService(db_session)

@pytest.fixture()
def activity_service(db_session):
    return ActivityService(db_session)

@pytest.fixture()
def user_service(db_session):
    return UserService(db_session)

@pytest.fixture()
def auth_service(db_session):
    return AuthService(db_session)

@pytest.fixture()
def admin_user(db_session):
    user = UserDB(
        username="adminuser",
        hashed_password=hash_password("12345678"),
        role=Roles.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def manager_user(db_session):
    user = UserDB(
        username="manageruser",
        hashed_password=hash_password("12345678"),
        role=Roles.MANAGER,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def sales_user(db_session):
    user = UserDB(
        username="salesuser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def owner_user(db_session):
    """Mesmo que sales_user, mas com nome owner para consistência."""
    user = UserDB(
        username="owner",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def foreign_user(db_session):
    user = UserDB(
        username="foreignuser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def existing_user(db_session):
    user = UserDB(
        username="testuser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def other_user_in_db(db_session):
    user = UserDB(
        username="otheruser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture()
def admin_context(admin_user):
    return SimpleNamespace(id=admin_user.id, role="admin")

@pytest.fixture()
def manager_context(manager_user):
    return SimpleNamespace(id=manager_user.id, role="manager")

@pytest.fixture()
def sales_context(sales_user):
    return SimpleNamespace(id=sales_user.id, role="sales")

@pytest.fixture()
def owner_context(owner_user):
    return SimpleNamespace(id=owner_user.id, role="sales")

@pytest.fixture()
def foreign_context(foreign_user):
    return SimpleNamespace(id=foreign_user.id, role="sales")

@pytest.fixture()
def current_user(existing_user):
    return SimpleNamespace(id=existing_user.id, username=existing_user.username, role="sales")

@pytest.fixture()
def another_user(other_user_in_db):
    return SimpleNamespace(id=other_user_in_db.id, username=other_user_in_db.username)

@pytest.fixture()
def company(db_session):
    company = CompanyDB(
        name="company one",
        cnpj="03.351.795/1801-36",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture()
def second_company(db_session):
    company = CompanyDB(
        name="company two",
        cnpj="85.308.670/0451-42",
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

@pytest.fixture()
def all_companies(company, second_company):
    return [company, second_company]

@pytest.fixture()
def empty_companies_db(db_session):
    for item in db_session.query(CompanyDB).all():
        db_session.delete(item)
    db_session.commit()
    return db_session

@pytest.fixture()
def company_payload():
    return CompanyCreate(
        name="Company One",
        cnpj="03.351.795/1801-36",
    )

@pytest.fixture()
def company_update_payload():
    return CompanyUpdate(
        name="Company Updated",
        cnpj="85.308.670/0451-42",
    )

@pytest.fixture()
def company_name_update_payload():
    return CompanyUpdate(name="Company Renamed")

@pytest.fixture()
def duplicate_company_payload(company):
    return CompanyCreate(
        name="Another Company",
        cnpj=company.cnpj,
    )

@pytest.fixture()
def renamed_company_payload(company):
    return CompanyCreate(
        name=company.name,
        cnpj=company.cnpj,
    )

@pytest.fixture()
def owner_lead(db_session, owner_user, company):
    lead = LeadsDB(
        name="Lead Owner",
        email="lead-owner@example.com",
        phone="11999999999",
        user_id=owner_user.id,
        company_id=company.id,
        status=StatusLeads.NEW,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        is_active=True,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead

@pytest.fixture()
def foreign_lead(db_session, foreign_user, company):
    lead = LeadsDB(
        name="Foreign Lead",
        email="foreign@example.com",
        phone="11888888888",
        user_id=foreign_user.id,
        company_id=company.id,
        status=StatusLeads.NEW,
        subject="Foreign Subject",
        description="Foreign Description",
        estimated_value=250.0,
        is_active=True,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead

@pytest.fixture()
def owner_leads(owner_lead):
    return owner_lead

@pytest.fixture()
def foreign_leads(foreign_lead):
    return [foreign_lead]

@pytest.fixture()
def empty_leads_db(db_session):
    for item in db_session.query(LeadsDB).all():
        db_session.delete(item)
    db_session.commit()
    return db_session

@pytest.fixture()
def lead_payload(company):
    return LeadCreate(
        name="Lead One",
        email="lead1@example.com",
        phone="11999999999",
        company_id=company.id,
        subject="Subject",
        description="Description",
        estimated_value=100.0,
        status=StatusLeads.NEW,
    )

@pytest.fixture()
def second_lead_payload(company):
    return LeadCreate(
        name="Lead Two",
        email="lead2@example.com",
        phone="11988888888",
        company_id=company.id,
        subject="Subject",
        description="Description",
        estimated_value=150.0,
        status=StatusLeads.NEW,
    )

@pytest.fixture()
def foreign_lead_payload(company):
    return LeadCreate(
        name="Foreign Lead",
        email="foreign-created@example.com",
        phone="11888888888",
        company_id=company.id,
        subject="Foreign Subject",
        description="Foreign Description",
        estimated_value=250.0,
        status=StatusLeads.NEW,
    )

@pytest.fixture()
def lead_update_payload(owner_lead):
    return LeadUpdate(
        name="Lead Updated",
        email="updated@example.com",
        phone="11977777777",
        company_id=owner_lead.company_id,
        status=StatusLeads.CONTACTED,
        subject="Updated Subject",
        description="Updated Description",
        estimated_value=200.0,
        is_active=False,
    )

@pytest.fixture()
def lead_update_missing_payload():
    return LeadUpdate(
        name="Lead Updated",
        email="updated@example.com",
        company_id=None,
        status=StatusLeads.CONTACTED,
    )

@pytest.fixture()
def lead_update_foreign_payload(owner_lead):
    return LeadUpdate(
        name="Lead Updated",
        email="updated@example.com",
        company_id=owner_lead.company_id,
        status=StatusLeads.CONTACTED,
    )

@pytest.fixture()
def lead_create_with_existing_email(company, lead):
    return LeadCreate(
        name="Other Lead",
        email=lead.email,
        phone="11988888888",
        company_id=company.id,
        subject="Subject",
        description="Description",
        estimated_value=150.0,
        status=StatusLeads.NEW,
    )

@pytest.fixture()
def lead(leads_service, owner_context, lead_payload):
    return leads_service.create_lead(owner_context, lead_payload)

@pytest.fixture()
def foreign_lead_created(leads_service, foreign_context, foreign_lead_payload):
    return leads_service.create_lead(foreign_context, foreign_lead_payload)

@pytest.fixture()
def owner_proposals(db_session, owner_user, owner_lead):
    proposal1 = ProposalDB(
        lead_id=owner_lead.id,
        user_id=owner_user.id,
        status=StatusProposalDB.PENDING,
        value=150.0,
        sent_at=None
    )
    db_session.add(proposal1)
    db_session.commit()
    db_session.refresh(proposal1)

    return proposal1

@pytest.fixture()
def foreign_proposal(db_session, foreign_user, foreign_lead):
    proposal = ProposalDB(lead_id=foreign_lead.id, user_id=foreign_user.id, status=StatusProposalDB.PENDING, value=220.0, sent_at=None)
    db_session.add(proposal)
    db_session.commit()
    db_session.refresh(proposal)
    return proposal

@pytest.fixture()
def empty_proposals_db(db_session):
    for item in db_session.query(ProposalDB).all():
        db_session.delete(item)
    db_session.commit()
    return db_session

@pytest.fixture()
def proposal_payload(owner_lead):
    return ProposalCreate(lead_id=owner_lead.id, status=StatusProposalDB.PENDING, value=150.0, sent_at=None)

@pytest.fixture()
def proposal_update_payload():
    return ProposalUpdate(status=StatusProposalDB.ACCEPTED, value=250.0)

@pytest.fixture()
def proposal_empty_status_payload(owner_lead):
    return SimpleNamespace(lead_id=owner_lead.id, status="", value=150.0, sent_at=None)

@pytest.fixture()
def proposal_empty_value_payload(owner_lead):
    return SimpleNamespace(lead_id=owner_lead.id, status=StatusProposalDB.ACCEPTED, value="", sent_at=None)

@pytest.fixture()
def proposal_negative_value_payload(owner_lead):
    return SimpleNamespace(lead_id=owner_lead.id, status=StatusProposalDB.ACCEPTED, value=-10.0, sent_at=None)

@pytest.fixture()
def owner_activities(db_session, owner_user, owner_lead):
    activity1 = ActivityDB(lead_id=owner_lead.id, user_id=owner_user.id, description="Ligacao 1", activity_type=ActivityType.CALL, done_at=None)
    db_session.add(activity1)
    db_session.commit()
    db_session.refresh(activity1)
    return activity1

@pytest.fixture()
def foreign_activity(db_session, foreign_user, foreign_lead):
    activity = ActivityDB(lead_id=foreign_lead.id, user_id=foreign_user.id, description="Ligacao externa", activity_type=ActivityType.CALL, done_at=None)
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity

@pytest.fixture()
def empty_activities_db(db_session):
    for item in db_session.query(ActivityDB).all():
        db_session.delete(item)
    db_session.commit()
    return db_session

@pytest.fixture()
def activity_payload(owner_lead):
    return ActivityCreate(lead_id=owner_lead.id, description="Ligacao de acompanhamento", activity_type=ActivityType.CALL, done_at=None)

@pytest.fixture()
def activity_update_payload():
    return ActivityUpdate(description="Ligacao atualizada", activity_type=ActivityType.EMAIL)

@pytest.fixture()
def activity_empty_type_payload(owner_lead):
    return SimpleNamespace(lead_id=owner_lead.id, description="Ligacao de acompanhamento", activity_type="", done_at=None)

@pytest.fixture()
def update_username_payload():
    return SimpleNamespace(username="newusername")

@pytest.fixture()
def update_password_payload():
    return SimpleNamespace(current_password="12345678", new_password="87654321")

@pytest.fixture()
def auth_payload():
    return SimpleNamespace(
        username="testuser",
        password="12345678",
        role=Roles.SALES,
        is_active=True,
        name="Test User",
    )

@pytest.fixture()
def auth_form_data():
    return SimpleNamespace(username="testuser", password="12345678")

@pytest.fixture()
def auth_payload_uppercase():
    return SimpleNamespace(
        username="TESTUSER",
        password="12345678",
        role=Roles.SALES,
        is_active=True,
        name="Test User",
    )

@pytest.fixture(scope="function")
def client():
    return TestClient(app)

@pytest.fixture(scope="function", autouse=True)
def override_db_for_http(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="function")
def auth_headers(admin_user):
    """
    Retorna headers de autenticação para um usuário admin.
    Para usar em testes HTTP, precisa gerar um token JWT real.
    """
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": admin_user.username, "ver": admin_user.token_version})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_headers_manager(manager_user):
    """Headers de autenticação para usuário manager."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": manager_user.username, "ver": manager_user.token_version})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_headers_sales(sales_user):
    """Headers de autenticação para usuário sales."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": sales_user.username, "ver": sales_user.token_version})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_headers_owner(owner_user):
    """Headers de autenticação para usuário owner (sales)."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": owner_user.username, "ver": owner_user.token_version})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(scope="function")
def auth_headers_foreign(foreign_user):
    """Headers de autenticação para usuário foreign (sales)."""
    from app.core.security import create_access_token
    token = create_access_token(data={"sub": foreign_user.username, "ver": foreign_user.token_version})
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture()
def http_company_payload():
    """Payload para criar empresa via HTTP."""
    return {
        "name": "http company",
        "cnpj": "42.028.355/1187-25"
    }

@pytest.fixture()
def http_company_update_payload():
    """Payload para atualizar empresa via HTTP."""
    return {
        "name": "HTTP Company Updated",
        "cnpj": "49.991.432/7712-88"
    }

@pytest.fixture()
def http_lead_payload(company):
    """Payload para criar lead via HTTP."""
    return {
        "name": "http lead",
        "email": "http-lead@example.com",
        "phone": "11999999999",
        "company_id": company.id,
        "subject": "HTTP Subject",
        "description": "HTTP Description",
        "estimated_value": 100.0,
        "status": "new"
    }

@pytest.fixture()
def http_lead_update_payload(company):
    """Payload para atualizar lead via HTTP."""
    return {
        "name": "HTTP Lead Updated",
        "email": "http-lead-updated@example.com",
        "phone": "11888888888",
        "company_id": company.id,
        "status": "contacted",
        "estimated_value": 200.0,
        "is_active": False
    }

@pytest.fixture()
def http_proposal_payload(owner_lead):
    """Payload para criar proposal via HTTP."""
    return {
        "lead_id": owner_lead.id,
        "status": "pending",
        "value": 150.0,
        "sent_at": None
    }

@pytest.fixture()
def http_proposal_update_payload():
    """Payload para atualizar proposal via HTTP."""
    return {
        "status": "accepted",
        "value": 250.0
    }

@pytest.fixture()
def http_activity_payload(owner_lead):
    """Payload para criar activity via HTTP."""
    return {
        "lead_id": owner_lead.id,
        "description": "HTTP Activity",
        "activity_type": "call",
        "done_at": None
    }

@pytest.fixture()
def http_activity_update_payload():
    """Payload para atualizar activity via HTTP."""
    return {
        "description": "HTTP Activity Updated",
        "activity_type": "email"
    }

@pytest.fixture()
def http_user_update_username_payload():
    """Payload para atualizar username via HTTP."""
    return {
        "username": "new_http_username"
    }

@pytest.fixture()
def http_user_update_password_payload():
    """Payload para atualizar password via HTTP."""
    return {
        "current_password": "12345678",
        "new_password": "87654321"
    }

@pytest.fixture()
def http_auth_register_payload():
    """Payload para registrar usuário via HTTP."""
    return {
        "username": "http_new_user",
        "password": "http_password123",
        "role": "SALES",
        "is_active": True,
        "name": "HTTP New User"
    }

@pytest.fixture()
def http_auth_login_form_data():
    """Form data para login via HTTP (OAuth2)."""
    return {
        "username": "adminuser",
        "password": "12345678"
    }