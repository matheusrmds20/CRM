from sqlalchemy.orm import Session

from app.api.exceps import BadRequestError, ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError
from app.repositories.leads import LeadsRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.proposals import ProposalCreate, ProposalUpdate


class ProposalService:
    def __init__(self, db: Session):
        self.repository = ProposalRepository(db)
        self.leads_repository = LeadsRepository(db)

    def _can_manage(self, user, owner_id):
        return user.role in ("admin", "manager") or user.id == owner_id

    def create_proposal(self, user, data: ProposalCreate):
        if data.status == "":
            raise BadRequestError("Nenhum tipo de proposal foi selecionado")

        if data.value == "":
            raise BadRequestError("Nenhum valor de proposal foi selecionado")

        if data.value < 0:
            raise BadRequestError("Valor de proposal deve ser maior que zero")

        lead = self.leads_repository.get_lead_by_id(data.lead_id, user.id)
        if not lead:
            raise ItemNotFoundError("Lead nao encontrado")

        if lead.user_id != user.id:
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        proposal_already_exists = self.repository.get_proposal_by_lead_id(user.id, data.lead_id)
        if proposal_already_exists:
            raise ItemAlreadyExistsError("Proposal ja existe")

        return self.repository.create_proposal(user.id, data)

    def get_proposal_by_id(self, user, proposal_id: int):
        proposal = self.repository.get_proposal_by_id(user.id, proposal_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not self._can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return proposal

    def get_proposal_by_lead_id(self, user, lead_id: int):
        proposal = self.repository.get_proposal_by_lead_id(user.id, lead_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not self._can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return proposal

    def get_proposal_by_user_id(self, user):
        proposals = self.repository.get_proposal_by_user_id(user.id)
        if not proposals:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        return proposals

    def get_all_proposals(self, user):
        proposals = self.repository.get_all_proposals(user.id)
        if not proposals:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        return proposals

    def update_proposal(self, proposal_id: int, user, data: ProposalUpdate):
        proposal = self.repository.get_proposal_by_id(user.id, proposal_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not self._can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        if data.status == "":
            raise BadRequestError("Nenhum tipo de proposal foi selecionado")

        if data.value == "":
            raise BadRequestError("Nenhum valor de proposal foi selecionado")

        if data.value < 0:
            raise BadRequestError("Valor de proposal deve ser maior que zero")

        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(proposal, field, value)

        return self.repository.update_proposal(proposal)

    def delete_proposal(self, proposal_id: int, user):
        proposal = self.repository.get_proposal_by_id(user.id, proposal_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not self._can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_proposal(proposal)
