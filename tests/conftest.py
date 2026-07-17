import os
import sys
from pathlib import Path

os.environ['DEBUG'] = 'false'

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.db.database import Base
import app.models.users
import app.models.companies
import app.models.leads
import app.models.activities
import app.models.proposals


TEST_DATABASE_URL = 'sqlite://'

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
)

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
        transaction.rollback()
        connection.close()


@pytest.fixture()
def sample_user(db_session):
    from app.models.users import UserDB, Roles

    user = UserDB(
        username='testuser',
        hashed_password='hashed_password',
        role=Roles.SALES,
        is_superuser=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def sample_company(db_session):
    from app.models.companies import CompanyDB

    company = CompanyDB(
        name='Test Company',
        cnpj='12.345.678/0001-90',
    )
    db_session.add(company)
    db_session.commit()
    db_session.refresh(company)
    return company

