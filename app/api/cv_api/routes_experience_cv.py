from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, Experience
from app.schemas.cv import ExperienceRequest, ExperienceSaveRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import generate_experience_from_ai

router = APIRouter()


@router.post("/api/experiences/", tags=["Experience Management"])
async def create_experience(
    request: ExperienceRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
    header = result.scalars().first()
    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    ExperienceRequest.validate_dates(request.start_date, request.end_date)

    experience = Experience(**request.dict(exclude={"header_id"}), header_id=header.id)
    db.add(experience)
    await db.commit()
    await db.refresh(experience)

    return success_response(code=201, data={
        "message": "Experience created successfully",
        "experience": serialize_sqlalchemy_object(experience)
    })


@router.get("/api/experiences/{experience_id}/", tags=["Experience Management"])
async def get_experience(
    experience_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    return success_response(code=200, data={"experience": serialize_sqlalchemy_object(experience)})


@router.put("/api/experiences/{experience_id}/", tags=["Experience Management"])
async def update_experience(
    experience_id: int,
    request: ExperienceRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    request.validate_dates(request.start_date, request.end_date)
    for key, value in request.dict(exclude_unset=True).items():
        setattr(experience, key, value)

    await db.commit()
    await db.refresh(experience)
    return success_response(code=200, data={"message": "Experience updated successfully", "experience": serialize_sqlalchemy_object(experience)})


@router.delete("/api/experiences/{experience_id}/", tags=["Experience Management"])
async def delete_experience(
    experience_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Experience).where(Experience.id == experience_id)
    result = await db.execute(stmt)
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    await db.delete(experience)
    await db.commit()

    return success_response(code=200, data={"message": "Experience deleted successfully"})


@router.post("/api/experiences/suggestions/", tags=["AI Enhancements"])
async def generate_experience_suggestions(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        result = await db.execute(select(Experience).where(Experience.header_id == header.id))
        experience = result.scalars().first()
        if not experience:
            return error_response(code=404, error_message="Experience not found for this user.")

        ai_suggestions = await generate_experience_from_ai(
            role=experience.role,
            start_date=experience.start_date,
            end_date=experience.end_date
        )

        return success_response(code=200, data={
            "experience_id": experience.id,
            "role": experience.role,
            "suggestions": ai_suggestions
        })

    except Exception as e:
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/experiences/save-description/{experience_id}/", tags=["AI Enhancements"])
async def save_experience_description(
    experience_id: int,
    request: ExperienceSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        experience = await db.get(Experience, experience_id)
        if not experience:
            return error_response(code=404, error_message="Experience not found.")

        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()
        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if experience.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this experience.")

        experience.description = request.selected_description
        await db.commit()
        await db.refresh(experience)

        return success_response(code=200, data={
            "experience_id": experience.id,
            "description": request.selected_description
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Error updating experience description", data=str(e))
