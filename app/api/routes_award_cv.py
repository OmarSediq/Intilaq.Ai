from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, Awards
from app.schemas.cv import AwardsRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object

router = APIRouter()


@router.post("/api/awards/", tags=["Volunteering & Awards"])
async def create_award(
    request: AwardsRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        award = Awards(
            **request.dict(exclude={"header_id"}),
            header_id=header.id
        )

        db.add(award)
        await db.commit()
        await db.refresh(award)

        return success_response(code=201, data={
            "message": "Award created successfully",
            "data": serialize_sqlalchemy_object(award)
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.get("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
async def get_award(
    award_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        award = await db.get(Awards, award_id)
        if not award:
            return error_response(code=404, error_message="Award not found")

        header = await db.get(Header, award.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to access this award.")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(award)})

    except Exception as e:
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.delete("/api/awards/{award_id}/", tags=["Volunteering & Awards"])
async def delete_award(
    award_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        award = await db.get(Awards, award_id)
        if not award:
            return error_response(code=404, error_message="Award not found")

        header = await db.get(Header, award.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to delete this award.")

        await db.delete(award)
        await db.commit()

        return success_response(code=200, data={"message": "Award deleted successfully"})

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")
