from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, VolunteeringExperience
from app.schemas.cv import VolunteeringRequest, SaveVolunteeringRequest, GenerateVolunteeringRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import generate_volunteering_description_from_ai

router = APIRouter()


@router.post("/api/volunteerings/", tags=["Volunteering & Awards"])
async def create_volunteering(
    request: VolunteeringRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        volunteering = VolunteeringExperience(
            **request.dict(exclude={"header_id"}),
            header_id=header.id
        )

        db.add(volunteering)
        await db.commit()
        await db.refresh(volunteering)

        return success_response(code=201, data={
            "message": "Volunteering experience created successfully",
            "data": serialize_sqlalchemy_object(volunteering)
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.get("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
async def get_volunteering(
    volunteering_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        volunteering = await db.get(VolunteeringExperience, volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await db.get(Header, volunteering.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to view this volunteering experience.")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(volunteering)})

    except Exception as e:
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.delete("/api/volunteerings/{volunteering_id}/", tags=["Volunteering & Awards"])
async def delete_volunteering(
    volunteering_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        volunteering = await db.get(VolunteeringExperience, volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await db.get(Header, volunteering.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to delete this volunteering experience.")

        await db.delete(volunteering)
        await db.commit()

        return success_response(code=200, data={"message": "Volunteering experience deleted successfully"})

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.post("/api/volunteerings-suggestions/", tags=["AI Enhancements"])
async def generate_volunteering_suggestions(
    request: GenerateVolunteeringRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        volunteering = await db.get(VolunteeringExperience, request.volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        header = await db.get(Header, volunteering.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to generate AI suggestions for this volunteering experience.")

        ai_suggestions = await generate_volunteering_description_from_ai(volunteering.role)

        return success_response(code=200, data={
            "message": "AI suggestions generated successfully",
            "suggestions": serialize_sqlalchemy_object(ai_suggestions)
        })

    except Exception as e:
        return error_response(code=500, error_message=f"Unexpected error: {str(e)}")


@router.put("/api/volunteerings-save-description/{volunteering_id}/", tags=["AI Enhancements"])
async def save_volunteering_description(
    volunteering_id: int,
    request: SaveVolunteeringRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        volunteering = await db.get(VolunteeringExperience, volunteering_id)
        if not volunteering:
            return error_response(code=404, error_message="Volunteering experience not found")

        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if volunteering.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this volunteering experience.")

        volunteering.description = request.selected_description
        await db.commit()
        await db.refresh(volunteering)

        return success_response(code=200, data={
            "message": "Volunteering description updated successfully",
            "description": volunteering.description
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message=f"Error updating volunteering description: {str(e)}")
