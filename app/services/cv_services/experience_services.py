from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header, Experience
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import generate_experience_from_ai


async def get_user_header(user_id: int, db: AsyncSession):
    result = await db.execute(select(Header).where(Header.user_id == int(user_id)))
    return result.scalars().first()


async def create_experience_service(request, user_id: int, db: AsyncSession):
    header = await get_user_header(user_id, db)
    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    request.validate_dates(request.start_date, request.end_date)

    experience = Experience(**request.dict(exclude={"header_id"}), header_id=header.id)
    db.add(experience)
    await db.commit()
    await db.refresh(experience)

    return success_response(code=201, data={
        "message": "Experience created successfully",
        "experience": serialize_sqlalchemy_object(experience)
    })


async def get_experience_service(experience_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(select(Experience).where(Experience.id == experience_id))
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    return success_response(code=200, data={"experience": serialize_sqlalchemy_object(experience)})


async def update_experience_service(experience_id: int, request, user_id: int, db: AsyncSession):
    result = await db.execute(select(Experience).where(Experience.id == experience_id))
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    request.validate_dates(request.start_date, request.end_date)

    for key, value in request.dict(exclude_unset=True).items():
        setattr(experience, key, value)

    await db.commit()
    await db.refresh(experience)
    return success_response(code=200, data={
        "message": "Experience updated successfully",
        "experience": serialize_sqlalchemy_object(experience)
    })


async def delete_experience_service(experience_id: int, user_id: int, db: AsyncSession):
    result = await db.execute(select(Experience).where(Experience.id == experience_id))
    experience = result.scalars().first()
    if not experience:
        return error_response(code=404, error_message="Experience not found")

    header = await db.get(Header, experience.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this experience")

    await db.delete(experience)
    await db.commit()

    return success_response(code=200, data={"message": "Experience deleted successfully"})


async def generate_experience_suggestions_service(user_id: int, db: AsyncSession):
    header = await get_user_header(user_id, db)
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


async def save_experience_description_service(experience_id: int, description: str, user_id: int, db: AsyncSession):
    experience = await db.get(Experience, experience_id)
    if not experience:
        return error_response(code=404, error_message="Experience not found.")

    header = await get_user_header(user_id, db)
    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    if experience.header_id != header.id:
        return error_response(code=403, error_message="Unauthorized access to this experience.")

    experience.description = description
    await db.commit()
    await db.refresh(experience)

    return success_response(code=200, data={
        "experience_id": experience.id,
        "description": description
    })
