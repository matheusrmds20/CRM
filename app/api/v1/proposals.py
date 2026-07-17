from fastapi import APIRouter, Depends
from app.services.proposals import ProposalService
from app.schemas.proposals import ProposalCreate, ProposalResponse, ProposalUpdate
from app.api.deps import get_current_user
from app.models.users import UserDB
from app.api.deps import get_db
from sqlalchemy.orm import Session

router_proposals = APIRouter(prefix="/proposals", tags=["proposals"])

@router_proposals.post("/create", response_model=ProposalResponse)
def create_proposal(
    data: ProposalCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)


    return service.create_proposal(current_user, data)

@router_proposals.get("", response_model=list[ProposalResponse])
def get_all_proposals(
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)

    return service.get_all_proposals(current_user)
    
@router_proposals.get("/id/{proposal_id}", response_model=ProposalResponse)
def get_proposal_by_id(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)
    
    return service.get_proposal_by_id(current_user, proposal_id)

@router_proposals.get("/lead_id/{lead_id}", response_model=ProposalResponse)
def get_proposal_by_lead_id(
    lead_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)

    return service.get_proposal_by_lead_id(current_user, lead_id)        

@router_proposals.get("/user_id/{user_id}", response_model=list[ProposalResponse])
def get_proposal_by_user_id(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)

    return service.get_proposal_by_user_id(user_id)

@router_proposals.patch("/{proposal_id}", response_model=ProposalUpdate)
def update_proposal(
    proposal_id: int,
    data: ProposalUpdate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)

    return service.update_proposal(proposal_id, current_user, data)

@router_proposals.delete("/{proposal_id}")
def delete_proposal(
    proposal_id: int,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(get_current_user),
):
    service = ProposalService(db)

    return service.delete_proposal(proposal_id, current_user)

