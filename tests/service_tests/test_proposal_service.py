from types import SimpleNamespace

import pytest

from app.api.exceps import BadRequestError, ItemNotFoundError, NoPermissionError

from app.models.proposals import StatusProposal

from app.schemas.proposals import ProposalCreate, ProposalUpdate



def test_create_proposal_success(proposal_service, owner_context, proposal_payload):
    result = proposal_service.create_proposal(owner_context, proposal_payload)
    assert result.id is not None
    assert result.lead_id == proposal_payload.lead_id
    assert result.user_id == owner_context.id
    assert result.status == proposal_payload.status
    assert result.value == proposal_payload.value


def test_create_proposal_raises_no_permission_for_foreign_lead(proposal_service, owner_context, foreign_lead):
    payload = ProposalCreate(lead_id=foreign_lead.id, status=StatusProposal.PENDING, value=150.0, sent_at=None)
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        proposal_service.create_proposal(owner_context, payload)


def test_create_proposal_raises_item_not_found_when_lead_missing(proposal_service, owner_context):
    payload = ProposalCreate(lead_id=9999, status=StatusProposal.PENDING, value=150.0, sent_at=None)
    with pytest.raises(ItemNotFoundError, match="Lead nao encontrado"):
        proposal_service.create_proposal(owner_context, payload)


def test_get_proposal_by_id_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    result = proposal_service.get_proposal_by_id(owner_context, proposal.id)
    assert result.id == proposal.id
    assert result.user_id == owner_context.id


def test_get_proposal_by_id_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.get_proposal_by_id(owner_context, 9999)


def test_get_proposal_by_lead_id_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    result = proposal_service.get_proposal_by_lead_id(owner_context, proposal.lead_id)
    assert len(result) >= 1
    assert result[0].id == proposal.id
    assert result[0].lead_id == proposal.lead_id


def test_get_proposal_by_lead_id_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.get_proposal_by_lead_id(owner_context, 9999)


def test_get_proposal_by_user_id_success(proposal_service, owner_context, owner_proposals):
    result = proposal_service.get_proposal_by_user_id(owner_context)
    assert len(result) == 1
    assert all(proposal.user_id == owner_context.id for proposal in result)


def test_get_proposal_by_user_id_raises_when_empty(proposal_service, foreign_context, empty_proposals_db):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.get_proposal_by_user_id(foreign_context)


def test_get_all_proposals_success(proposal_service, owner_context, owner_proposals):
    result = proposal_service.get_all_proposals(owner_context)
    assert len(result) == 1
    assert all(proposal.user_id == owner_context.id for proposal in result)


def test_get_all_proposals_admin_can_access_owner_records(proposal_service, admin_context, owner_proposals):
    result = proposal_service.get_all_proposals(admin_context)
    assert len(result) == 1


def test_get_all_proposals_raises_when_empty(proposal_service, foreign_context, empty_proposals_db):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.get_all_proposals(foreign_context)


def test_update_proposal_success(proposal_service, owner_context, proposal_payload, proposal_update_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    result = proposal_service.update_proposal(proposal.id, owner_context, proposal_update_payload)
    assert result.id == proposal.id
    assert result.status == StatusProposal.ACCEPTED
    assert result.value == 250.0


def test_update_proposal_raises_item_not_found(proposal_service, owner_context, proposal_update_payload):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.update_proposal(9999, owner_context, proposal_update_payload)


def test_update_proposal_raises_no_permission_when_foreign_user(proposal_service, owner_context, foreign_proposal, proposal_update_payload):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        proposal_service.update_proposal(foreign_proposal.id, owner_context, proposal_update_payload)


def test_delete_proposal_success(proposal_service, owner_context, proposal_payload):
    proposal = proposal_service.create_proposal(owner_context, proposal_payload)
    result = proposal_service.delete_proposal(proposal.id, owner_context)
    assert result.id == proposal.id


def test_delete_proposal_raises_item_not_found(proposal_service, owner_context):
    with pytest.raises(ItemNotFoundError, match="Nenhum proposal encontrado"):
        proposal_service.delete_proposal(9999, owner_context)


def test_delete_proposal_raises_no_permission_when_foreign_user(proposal_service, owner_context, foreign_proposal):
    with pytest.raises(NoPermissionError, match="Voce nao tem permissao para executar essa acao"):
        proposal_service.delete_proposal(foreign_proposal.id, owner_context)