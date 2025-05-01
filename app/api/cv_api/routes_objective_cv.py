from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.auth_api.auth.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, Objective
from app.schemas.cv import ObjectiveSaveRequest
from app.utils.response_schemas import success_response, error_response
from app.services.ai_services import generate_objective_from_ai

router = APIRouter()

@router.post("/api/objectives/suggestions/", tags=["AI Enhancements"])
async def generate_objective_suggestions(
    request: ObjectiveSaveRequest, 
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")
        
        if not header.job_title or not header.years_of_experience:
            return error_response(code=400, error_message="Missing job title or years of experience in header.")

        db_objective = Objective(
            header_id=header.id,
            description=request.description or ""
        )

        db.add(db_objective)
        await db.commit()
        await db.refresh(db_objective)

        ai_suggestions = await generate_objective_from_ai(
            job_title=header.job_title,
            years_of_experience=header.years_of_experience
        )

        return success_response(code=200, data={
            "objective_id": db_objective.id,
            "header_id": header.id,
            "suggestions": ai_suggestions
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/objectives/save-description/{objective_id}/", tags=["AI Enhancements"])
async def save_objective_description(
    objective_id: int,
    request: ObjectiveSaveRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        objective = await db.get(Objective, objective_id)
        if not objective:
            return error_response(code=404, error_message="Objective not found.")

        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        if objective.header_id != header.id:
            return error_response(code=403, error_message="Unauthorized access to this objective.")

        objective.description = request.description
        await db.commit()
        await db.refresh(objective)

        return success_response(code=200, data={
            "objective_id": objective.id,
            "description": request.description
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Error updating objective description", data=str(e))
