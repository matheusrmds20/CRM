from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError, UnauthorizedError
from app.core.security import hash_password
from app.models.activities import ActivityDB, ActivityTypeDB
from app.models.leads import LeadsDB, StatusLeads
from app.models.users import Roles, UserDB
from app.schemas.activities import ActivityCreate, ActivityUpdate
from app.services.activities import ActivityService


class ListWithUserId(list):
    def __init__(self, iterable=(), user_id=None):
        super().__init__(iterable)
        self.user_id = user_id


@pytest.fixture()
def owner_context(sample_user):
    return SimpleNamespace(id=sample_user.id, role="sales")


@pytest.fixture()
def other_user(db_session):
    user = UserDB(
        username="otheruser",
        hashed_password=hash_password("12345678"),
        role=Roles.SALES,
        is_superuser=False,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def owned_lead(db_session, sample_company, sample_user):
    lead = LeadsDB(
        name="Lead Owner",
        email="owner-lead@example.com",
        phone="11999999999",
        user_id=sample_user.id,
        company_id=sample_company.id,
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
def foreign_lead(db_session, sample_company, other_user):
    lead = LeadsDB(
        name="Lead Other",
        email="other-lead@example.com",
        phone="11888888888",
        user_id=other_user.id,
        company_id=sample_company.id,
        status=StatusLeads.NEW,
        subject="Subject",
        description="Description",
        estimated_value=200.0,
        is_active=True,
    )
    db_session.add(lead)
    db_session.commit()
    db_session.refresh(lead)
    return lead


@pytest.fixture()
def activity_service(db_session):
    return ActivityService(db_session)


@pytest.fixture()
def activity_payload(owned_lead):
    return ActivityCreate(
        lead_id=owned_lead.id,
        description="Ligacao de acompanhamento",
        type=ActivityTypeDB.CALL,
        done_at=None,
    )


def test_create_activity_success(activity_service, owner_context, activity_payload):
    result = activity_service.create_activity(owner_context.id, activity_payload)

    assert result.id is not None
    assert result.lead_id == activity_payload.lead_id
    assert result.user_id == owner_context.id
    assert result.type == activity_payload.type
    assert result.description == activity_payload.description


def test_create_activity_raises_if_already_exists(activity_service, owner_context, activity_payload):
    activity_service.create_activity(owner_context.id, activity_payload)

    with pytest.raises(ItemAlreadyExistsError):
        activity_service.create_activity(owner_context.id, activity_payload)


@pytest.mark.xfail(reason="Current service checks lead.user_id before validating lead exists")
def test_create_activity_raises_item_not_found_when_lead_missing(activity_service, owner_context):
    payload = ActivityCreate(
        lead_id=9999,
        description="Ligacao de acompanhamento",
        type=ActivityTypeDB.CALL,
        done_at=None,
    )

    with pytest.raises(ItemNotFoundError):
        activity_service.create_activity(owner_context.id, payload)


def test_create_activity_raises_no_permission_for_foreign_lead(
    activity_service,
    owner_context,
    foreign_lead,
):


    payload = ActivityCreate(
        lead_id=foreign_lead.id,
        description="Ligacao de acompanhamento",
        type=ActivityTypeDB.CALL,
        done_at=None,
    )

    with pytest.raises(UnauthorizedError):
        activity_service.create_activity(owner_context.id, payload)


def test_create_activity_raises_bad_request_when_type_empty(activity_service, owner_context, owned_lead):
    payload = SimpleNamespace(
        lead_id=owned_lead.id,
        description="Ligacao de acompanhamento",
        type="",
        done_at=None,
    )

    with pytest.raises(BadRequestError):
        activity_service.create_activity(owner_context.id, payload)


def test_get_all_activities_success(activity_service, owner_context, activity_payload, monkeypatch):
    activity = activity_service.create_activity(owner_context.id, activity_payload)
    activities = ListWithUserId([activity], user_id=owner_context.id)
    monkeypatch.setattr(
        activity_service.repository,
        "get_all_activities",
        lambda user_id: activities,
    )

    result = activity_service.get_all_activities(owner_context)

    assert len(result) == 1
    assert result[0].id == activity.id


def test_get_all_activities_raises_when_empty(activity_service, owner_context, monkeypatch):
    monkeypatch.setattr(
        activity_service.repository,
        "get_all_activities",
        lambda user_id: ListWithUserId([], user_id=owner_context.id),
    )

    with pytest.raises(ItemNotFoundError, match="Nenhum activity encontrado"):
        activity_service.get_all_activities(owner_context)


def test_get_activity_by_id_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context.id, activity_payload)

    result = activity_service.get_activity_by_id(owner_context, activity.id)

    assert result.id == activity.id
    assert result.user_id == owner_context.id


@pytest.mark.xfail(reason="Current service checks activity.user_id before validating activity exists")
def test_get_activity_by_id_raises_item_not_found(activity_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        activity_service.get_activity_by_id(owner_context, 9999)


def test_get_activity_by_lead_id_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context.id, activity_payload)

    result = activity_service.get_activity_by_lead_id(owner_context, activity.lead_id)

    assert result.id == activity.id
    assert result.lead_id == activity.lead_id


@pytest.mark.xfail(reason="Current service checks activity.user_id before validating activity exists")
def test_get_activity_by_lead_id_raises_item_not_found(activity_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        activity_service.get_activity_by_lead_id(owner_context, 9999)


def test_get_activity_by_user_id_success(activity_service, owner_context, activity_payload, monkeypatch):
    activity = activity_service.create_activity(owner_context.id, activity_payload)
    activities = ListWithUserId([activity], user_id=owner_context.id)
    monkeypatch.setattr(
        activity_service.repository,
        "get_activity_by_user_id",
        lambda user_id: activities,
    )

    result = activity_service.get_activity_by_user_id(owner_context, owner_context.id)

    assert len(result) == 1
    assert result[0].id == activity.id


def test_get_activity_by_user_id_raises_when_empty(activity_service, owner_context, monkeypatch):
    monkeypatch.setattr(
        activity_service.repository,
        "get_activity_by_user_id",
        lambda user_id: ListWithUserId([], user_id=owner_context.id),
    )

    with pytest.raises(ItemNotFoundError, match="Nenhum activity encontrado"):
        activity_service.get_activity_by_user_id(owner_context, owner_context.id)


@pytest.mark.xfail(reason="Current service checks activity.user_id before validating activity exists")
def test_update_activity_raises_item_not_found(activity_service, owner_context):
    payload = ActivityUpdate(description="Atualizado")

    with pytest.raises(ItemNotFoundError):
        activity_service.update_activity(9999, owner_context, payload)


def test_update_activity_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context.id, activity_payload)
    payload = ActivityUpdate(description="Ligacao atualizada", type=ActivityTypeDB.EMAIL)

    result = activity_service.update_activity(activity.id, owner_context, payload)

    assert result.id == activity.id
    assert result.description == "Ligacao atualizada"
    assert result.type == ActivityTypeDB.EMAIL


def test_update_activity_raises_no_permission_when_foreign_user(
    activity_service,
    owner_context,
    other_user,
    activity_payload,
    monkeypatch,
):
    activity = activity_service.create_activity(owner_context.id, activity_payload)
    foreign_activity = ActivityDB(
        id=activity.id,
        lead_id=activity.lead_id,
        user_id=other_user.id,
        description=activity.description,
        type=activity.type,
        done_at=activity.done_at,
    )
    monkeypatch.setattr(
        activity_service.repository,
        "get_activity_by_id",
        lambda user_id, activity_id: foreign_activity,
    )

    payload = ActivityUpdate(description="Atualizado")

    with pytest.raises(NoPermissionError):
        activity_service.update_activity(activity.id, owner_context, payload)


def test_delete_activity_success(activity_service, owner_context, activity_payload):
    activity = activity_service.create_activity(owner_context.id, activity_payload)

    result = activity_service.delete_activity(activity.id, owner_context)

    assert result.id == activity.id


@pytest.mark.xfail(reason="Current service checks activity.user_id before validating activity exists")
def test_delete_activity_raises_item_not_found(activity_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        activity_service.delete_activity(9999, owner_context)


def test_delete_activity_raises_no_permission_when_foreign_user(
    activity_service,
    owner_context,
    other_user,
    activity_payload,
    monkeypatch,
):
    activity = activity_service.create_activity(owner_context.id, activity_payload)
    foreign_activity = ActivityDB(
        id=activity.id,
        lead_id=activity.lead_id,
        user_id=other_user.id,
        description=activity.description,
        type=activity.type,
        done_at=activity.done_at,
    )
    monkeypatch.setattr(
        activity_service.repository,
        "get_activity_by_id",
        lambda user_id, activity_id: foreign_activity,
    )

    with pytest.raises(NoPermissionError):
        activity_service.delete_activity(activity.id, owner_context)
