from fastapi import APIRouter, Depends
from app.services.proposals import ProposalService
from app.schemas.proposals import ProposalCreate, ProposalResponse, ProposalUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_proposals = APIRouter(prefix="/proposals", tags=["proposals"])

def get_proposals_service(db: Session = Depends(get_db)):
    return ProposalService(db)

@router_proposals.post(
    "/create",
    response_model=ProposalResponse,
    summary="Cria uma nova proposta",
    description="Cria uma proposta associada ao usuário autenticado.",
)
def create_proposal(
    data: ProposalCreate,
    service: ProposalService = Depends(get_proposals_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.create_proposal(current_user, data)

@router_proposals.get(
    "/lead_id/{lead_id}",
    response_model=list[ProposalResponse],
    summary="Lista propostas por lead",
    description="Retorna as propostas de um lead específico.",
)
def get_proposal_by_lead_id(
    lead_id: int,
    service: ProposalService = Depends(get_proposals_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.get_proposal_by_lead_id(current_user, lead_id)        

@router_proposals.patch(
    "/update/{proposal_id}",
    response_model=ProposalResponse,
    summary="Atualiza uma proposta",
    description="Atualiza os dados da proposta do usuário autenticado.",
)
def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    service: ProposalService = Depends(get_proposals_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.update_proposal(proposal_id, current_user, data)

@router_proposals.delete(
    "/delete/{proposal_id}",
    response_model=ProposalResponse,
    summary="Remove uma proposta",
    description="Remove a proposta do usuário autenticado pelo ID.",
)
def delete_proposal(
    proposal_id: int,
    service: ProposalService = Depends(get_proposals_service),
    current_user: UserDB = Depends(get_current_user),
):

    return service.delete_proposal(proposal_id, current_user)
