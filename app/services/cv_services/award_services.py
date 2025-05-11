from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException

from app.database.models.cv_section_models import Header, Awards
from app.schemas.cv import AwardsRequest


async def get_user_header(user_id: int, db: AsyncSession):
    result = await db.execute(select(Header).where(Header.user_id == int(user_id)))
    header = result.scalars().first()
    if not header:
        raise HTTPException(status_code=404, detail="Header not found for this user.")
    return header


async def create_award_service(user_id: int, request: AwardsRequest, db: AsyncSession):
    header = await get_user_header(user_id, db)

    award = Awards(
        **request.dict(exclude={"header_id"}),
        header_id=header.id
    )
    db.add(award)
    await db.commit()
    await db.refresh(award)
    return award



async def get_award_service(award_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)  

    award = await db.get(Awards, award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    header = await db.get(Header, award.header_id)
    if not header or header.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to access this award.")

    return award


async def delete_award_service(award_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)  

    award = await db.get(Awards, award_id)
    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    header = await db.get(Header, award.header_id)
    if not header or header.user_id != user_id:
        raise HTTPException(status_code=403, detail="You do not have permission to delete this award.")

    await db.delete(award)
    await db.commit()