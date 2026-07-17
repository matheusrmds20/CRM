from fastapi import APIRouter
from app.api.v1.auth import router_auth
from app.api.v1.users import router_user
from app.api.v1.leads import router_leads
from app.api.v1.activities import router_activities
from app.api.v1.proposals import router_proposals
from app.api.v1.companies import router_companies

router = APIRouter()

router.include_router(router_auth, prefix="", tags=["auth"])
router.include_router(router_user, prefix="", tags=["users"])
router.include_router(router_leads, prefix="", tags=["leads"])
router.include_router(router_activities, prefix="", tags=["activities"])
router.include_router(router_proposals, prefix="", tags=["proposals"])
router.include_router(router_companies, prefix="", tags=["companies"])