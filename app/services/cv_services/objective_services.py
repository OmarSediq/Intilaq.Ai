from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Header, Objective
from app.utils.response_schemas import success_response, error_response
from app.services.ai_services import generate_objective_from_ai


async def generate_objective_suggestions_service(request, user_id: int, db: AsyncSession):
    result = await db.execute(select(Header).where(Header.user_id == user_id))
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


async def save_objective_description_service(objective_id: int, description: str, user_id: int, db: AsyncSession):
    objective = await db.get(Objective, objective_id)
    if not objective:
        return error_response(code=404, error_message="Objective not found.")

    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()

    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    if objective.header_id != header.id:
        return error_response(code=403, error_message="Unauthorized access to this objective.")

    objective.description = description
    await db.commit()
    await db.refresh(objective)

    return success_response(code=200, data={
        "objective_id": objective.id,
        "description": description
    })
