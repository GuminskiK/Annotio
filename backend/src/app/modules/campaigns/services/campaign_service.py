from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.app.core.exceptions import CampaignNotFoundException
from src.app.modules.campaigns.models.Campaigns import (
    Campaign,
    CampaignCreate,
    CampaignUpdate,
)


async def create_campaign(session: AsyncSession, campaign: CampaignCreate, user_id: UUID):
    
    data = campaign.model_dump(exclude={"client_id"})
    db_campaign = Campaign(**data, client_id=user_id)
    session.add(db_campaign)
    await session.commit()
    await session.refresh(db_campaign)

    return db_campaign


async def fetch_campaign_by_id(session: AsyncSession, campaign_id: UUID):

    result = await session.exec(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.one_or_none()

    if not campaign:
        raise CampaignNotFoundException()

    return campaign


async def fetch_user_campaigns(session: AsyncSession, client_id: UUID):

    result = await session.exec(select(Campaign).where(Campaign.client_id == client_id))
    return result.all()

async def update_campaign(session: AsyncSession, campaign_update: CampaignUpdate, campaign_id: UUID, client_id: UUID):

    result = await session.exec(select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == client_id))
    db_campaign = result.one_or_none()

    if not db_campaign:
        raise CampaignNotFoundException()

    update_data = campaign_update.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(db_campaign, key, value)

    session.add(db_campaign)
    await session.commit()
    await session.refresh(db_campaign)

    return db_campaign


async def delete_campaign(session: AsyncSession, campaign_id: UUID, client_id: UUID):

    result = await session.exec(select(Campaign).where(Campaign.id == campaign_id, Campaign.client_id == client_id))
    db_campaign = result.one_or_none()

    if not db_campaign:
        raise CampaignNotFoundException()

    await session.delete(db_campaign)
    await session.commit()

