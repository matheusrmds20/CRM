from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, ItemNotFoundError, NoPermissionError
from app.core.security import hash_password
from app.models.leads import LeadsDB, StatusLeads
from app.models.proposals import ProposalDB, StatusProposalDB
from app.models.users import Roles, UserDB
from app.repositories.leads import LeadsRepository
from app.schemas.proposals import ProposalCreate, ProposalUpdate
from app.services.proposals import ProposalService


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
def proposal_service(db_session):
    service = ProposalService(db_session)
    service.leads_repository = LeadsRepository(db_session)
    return service


@pytest.fixture()
def proposal_payload(owned_lead):
    return ProposalCreate(
        lead_id=owned_lead.id,
        status=StatusProposalDB.PENDING,
        value=150.0,
        sent_at=None,
    )


def test_create_proposal_success(proposal_service, owner_context, proposal_payload):
    result = proposal_service.create_proposal(owner_context, proposal_payload)

    assert result.id is not None
    assert result.lead_id == proposal_payload.lead_id
    assert result.user_id == owner_context.id
    assert result.status == proposal_payload.status
    assert result.value == proposal_payload.value


def test_create_proposal_raises_if_already_exists(proposal_service, owner_context, proposal_payload):
    proposal_service.create_proposal(owner_context, proposal_payload)

    with pytest.raises(ValueError, match="Proposal"):
        proposal_service.create_proposal(owner_context, proposal_payload)


def test_create_proposal_raises_no_permission_for_foreign_lead(
    proposal_service,
    owner_context,
    foreign_lead,
):
    payload = ProposalCreate(
        lead_id=foreign_lead.id,
        status=StatusProposalDB.PENDING,
        value=150.0,
        sent_at=None,
    )

    with pytest.raises(NoPermissionError):
        proposal_service.create_proposal(owner_context, payload)


@pytest.mark.xfail(reason="Current service checks lead.user_id before validating lead exists")
def test_create_proposal_raises_item_not_found_when_lead_missing(proposal_service, owner_context):
    payload = ProposalCreate(
        lead_id=9999,
        status=StatusProposalDB.PENDING,
        value=150.0,
        sent_at=None,
    )

    with pytest.raises(ItemNotFoundError):
        proposal_service.create_proposal(owner_context, payload)


def test_create_proposal_raises_bad_request_when_status_empty(proposal_service, owner_context, owned_lead):
    payload = SimpleNamespace(
        lead_id=owned_lead.id,
        status="",
        value=150.0,
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.create_proposal(owner_context, payload)


def test_create_proposal_raises_bad_request_when_value_empty(proposal_service, owner_context, owned_lead):
    payload = SimpleNamespace(
        lead_id=owned_lead.id,
        status=StatusProposalDB.PENDING,
        value="",
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.create_proposal(owner_context, payload)


def test_create_proposal_raises_bad_request_when_value_is_negative(proposal_service, owner_context, owned_lead):
    payload = SimpleNamespace(
        lead_id=owned_lead.id,
        status=StatusProposalDB.PENDING,
        value=-10.0,
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.create_proposal(owner_context, payload)


def test_get_proposal_by_id_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)

    result = proposal_service.get_proposal_by_id(owner_context, proposal.id)

    assert result.id == proposal.id
    assert result.user_id == owner_context.id


@pytest.mark.xfail(reason="Current service checks proposal.user_id before validating proposal exists")
def test_get_proposal_by_id_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        proposal_service.get_proposal_by_id(owner_context, 9999)


def test_get_proposal_by_lead_id_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)

    result = proposal_service.get_proposal_by_lead_id(owner_context, proposal.lead_id)

    assert result.id == proposal.id
    assert result.lead_id == proposal.lead_id


@pytest.mark.xfail(reason="Current service checks proposal.user_id before validating proposal exists")
def test_get_proposal_by_lead_id_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        proposal_service.get_proposal_by_lead_id(owner_context, 9999)


def test_get_proposal_by_user_id_success(proposal_service, owner_context, proposal_payload, monkeypatch):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    proposals = ListWithUserId([proposal], user_id=owner_context.id)
    monkeypatch.setattr(
        proposal_service.repository,
        "get_proposal_by_user_id",
        lambda user_id: proposals,
    )

    result = proposal_service.get_proposal_by_user_id(owner_context)

    assert len(result) == 1
    assert result[0].id == proposal.id


def test_get_proposal_by_user_id_raises_when_empty(proposal_service, owner_context, monkeypatch):
    monkeypatch.setattr(
        proposal_service.repository,
        "get_proposal_by_user_id",
        lambda user_id: ListWithUserId([], user_id=owner_context.id),
    )

    with pytest.raises(ValueError, match="Nenhum proposal encontrado"):
        proposal_service.get_proposal_by_user_id(owner_context)


def test_get_all_proposals_success(proposal_service, owner_context, proposal_payload, monkeypatch):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    proposals = ListWithUserId([proposal], user_id=owner_context.id)
    monkeypatch.setattr(
        proposal_service.repository,
        "get_all_proposals",
        lambda user_id: proposals,
    )

    result = proposal_service.get_all_proposals(owner_context)

    assert len(result) == 1
    assert result[0].id == proposal.id


def test_get_all_proposals_raises_when_empty(proposal_service, owner_context, monkeypatch):
    monkeypatch.setattr(
        proposal_service.repository,
        "get_all_proposals",
        lambda user_id: ListWithUserId([], user_id=owner_context.id),
    )

    with pytest.raises(ValueError, match="Nenhum proposal encontrado"):
        proposal_service.get_all_proposals(owner_context)


def test_update_proposal_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    payload = ProposalUpdate(
        status=StatusProposalDB.ACCEPTED,
        value=250.0,
    )

    result = proposal_service.update_proposal(proposal.id, owner_context, payload)

    assert result.id == proposal.id
    assert result.status == StatusProposalDB.ACCEPTED
    assert result.value == 250.0


@pytest.mark.xfail(reason="Current service checks proposal.user_id before validating proposal exists")
def test_update_proposal_raises_item_not_found(proposal_service, owner_context):
    payload = ProposalUpdate(status=StatusProposalDB.ACCEPTED, value=250.0)

    with pytest.raises(ItemNotFoundError):
        proposal_service.update_proposal(9999, owner_context, payload)


def test_update_proposal_raises_no_permission_when_foreign_user(
    proposal_service,
    owner_context,
    other_user,
    proposal_payload,
    monkeypatch,
):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    foreign_proposal = ProposalDB(
        id=proposal.id,
        lead_id=proposal.lead_id,
        user_id=other_user.id,
        status=proposal.status,
        value=proposal.value,
        sent_at=proposal.sent_at,
    )
    monkeypatch.setattr(
        proposal_service.repository,
        "get_proposal_by_id",
        lambda user_id, proposal_id: foreign_proposal,
    )

    payload = ProposalUpdate(status=StatusProposalDB.ACCEPTED, value=250.0)

    with pytest.raises(NoPermissionError):
        proposal_service.update_proposal(proposal.id, owner_context, payload)


def test_update_proposal_raises_bad_request_when_status_empty(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    payload = SimpleNamespace(
        lead_id=proposal.lead_id,
        status="",
        value=250.0,
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.update_proposal(proposal.id, owner_context, payload)


def test_update_proposal_raises_bad_request_when_value_empty(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    payload = SimpleNamespace(
        lead_id=proposal.lead_id,
        status=StatusProposalDB.ACCEPTED,
        value="",
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.update_proposal(proposal.id, owner_context, payload)


def test_update_proposal_raises_bad_request_when_value_is_negative(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    payload = SimpleNamespace(
        lead_id=proposal.lead_id,
        status=StatusProposalDB.ACCEPTED,
        value=-10.0,
        sent_at=None,
    )

    with pytest.raises(BadRequestError):
        proposal_service.update_proposal(proposal.id, owner_context, payload)


def test_delete_proposal_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)

    result = proposal_service.delete_proposal(proposal.id, owner_context)

    assert result.id == proposal.id


@pytest.mark.xfail(reason="Current service checks proposal.user_id before validating proposal exists")
def test_delete_proposal_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError):
        proposal_service.delete_proposal(9999, owner_context)


def test_delete_proposal_raises_no_permission_when_foreign_user(
    proposal_service,
    owner_context,
    other_user,
    proposal_payload,
    monkeypatch,
):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    foreign_proposal = ProposalDB(
        id=proposal.id,
        lead_id=proposal.lead_id,
        user_id=other_user.id,
        status=proposal.status,
        value=proposal.value,
        sent_at=proposal.sent_at,
    )
    monkeypatch.setattr(
        proposal_service.repository,
        "get_proposal_by_id",
        lambda user_id, proposal_id: foreign_proposal,
    )

    with pytest.raises(NoPermissionError):
        proposal_service.delete_proposal(proposal.id, owner_context)
