from uuid import UUID

from fastapi import APIRouter
from src.app.deps.dbs import db_session
from src.app.deps.users import CurrentUser
from src.app.modules.campaigns.models.Campaigns import (
    CampaignCreate,
    CampaignRead,
    CampaignUpdate,
)
from src.app.modules.campaigns.services.campaign_service import (
    create_campaign,
    delete_campaign,
    fetch_campaign_by_id,
    fetch_user_campaigns,
    update_campaign,
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

@router.post("", response_model=CampaignRead, status_code=201)
async def post_campaign(session: db_session, user: CurrentUser, campaign: CampaignCreate):
    return await create_campaign(session, campaign, user.user_id)

@router.get("/users/{user_id}", response_model=list[CampaignRead])
async def get_campaigns(session: db_session, user_id: UUID):
    return await fetch_user_campaigns(session, user_id)

@router.get("/{campaign_id}", response_model=CampaignRead)
async def get_campaign(session: db_session, campaign_id: UUID):
    return await fetch_campaign_by_id(session, campaign_id)

@router.patch("/{campaign_id}", response_model=CampaignRead)
async def patch_campaign(session: db_session, user: CurrentUser, campaign_id: UUID, update: CampaignUpdate):
    return await update_campaign(session, update, campaign_id, user.user_id)

@router.delete("/{campaign_id}", status_code=204)
async def remove_campaign(session: db_session, user: CurrentUser, campaign_id: UUID):
    return await delete_campaign(session, campaign_id, user.user_id)