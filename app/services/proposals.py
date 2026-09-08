from sqlalchemy.orm import Session

from app.api.exceps import BadRequestError, ItemAlreadyExistsError, ItemNotFoundError, NoPermissionError
from app.repositories.leads import LeadsRepository
from app.repositories.proposals import ProposalRepository
from app.schemas.proposals import ProposalCreate, ProposalUpdate
from app.utils.permissions import can_manage, can_manage_admin

class ProposalService:
    def __init__(self, db: Session):
        self.repository = ProposalRepository(db)
        self.leads_repository = LeadsRepository(db)


    def create_proposal(self, user, data: ProposalCreate):
        if data.status == "":
            raise BadRequestError("Nenhum tipo de proposal foi selecionado")


        lead = self.leads_repository.get_lead_by_id(data.lead_id)
        if not lead:
            raise ItemNotFoundError("Lead nao encontrado")

        if not can_manage(user, lead.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.create_proposal(user.id, data)

    def get_proposal_by_id(self, user, proposal_id: int):
        proposal = self.repository.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return proposal

    def get_proposal_by_lead_id(self, user, lead_id: int):
        proposals = self.repository.get_proposal_by_lead_id(lead_id)
        if not proposals:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not all(can_manage(user, p.user_id) for p in proposals):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return proposals

    def get_proposal_by_user_id(self, user, user_id: int = None):
        target_id = user.id if user_id is None else user_id

        if can_manage(user, target_id):
            proposals = self.repository.get_all_proposals(target_id)
        else:
            proposals = self.repository.get_all_proposals(user.id)

        if not proposals:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        return proposals

    def get_all_proposals(self, user):

        if can_manage_admin(user):
            proposals = self.repository.get_all_proposals()
        else:
            proposals = self.repository.get_all_proposals(user.id)

        if not proposals:
            raise ItemNotFoundError("Nenhum proposal encontrado")


        return proposals

    def update_proposal(self, proposal_id: int, user, data: ProposalUpdate):
        proposal = self.repository.get_proposal_by_id(proposal_id)


        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")


        if not can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")


        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(proposal, field, value)

        return self.repository.update_proposal(proposal)

    def delete_proposal(self, proposal_id: int, user):
        proposal = self.repository.get_proposal_by_id(proposal_id)
        if not proposal:
            raise ItemNotFoundError("Nenhum proposal encontrado")

        if not can_manage(user, proposal.user_id):
            raise NoPermissionError("Voce nao tem permissao para executar essa acao")

        return self.repository.delete_proposal(proposal)
