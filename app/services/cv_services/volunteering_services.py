from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Header, VolunteeringExperience
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from app.services.ai_services import generate_volunteering_description_from_ai


async def create_volunteering_service(request, user_id: int, db: AsyncSession):
    user_id = int(user_id)  
    result = await db.execute(select(Header).where(Header.user_id == user_id))
    header = result.scalars().first()
    if not header:
        return error_response(code=404, error_message="Header not found")

    volunteering = VolunteeringExperience(**request.dict(exclude={"header_id"}), header_id=header.id)
    db.add(volunteering)
    await db.commit()
    await db.refresh(volunteering)

    return success_response(code=201, data={
        "message": "Volunteering experience created successfully",
        "data": serialize_sqlalchemy_object(volunteering)
    })


async def get_volunteering_service(volunteering_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)  
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        return error_response(code=404, error_message="Volunteering experience not found")

    header = await db.get(Header, volunteering.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    return success_response(code=200, data={"data": serialize_sqlalchemy_object(volunteering)})


async def delete_volunteering_service(volunteering_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)  
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        return error_response(code=404, error_message="Volunteering experience not found")

    header = await db.get(Header, volunteering.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    await db.delete(volunteering)
    await db.commit()

    return success_response(code=200, data={"message": "Volunteering experience deleted successfully"})


async def generate_volunteering_suggestions_service(volunteering_id: int, user_id: int, db: AsyncSession):
    user_id = int(user_id)  
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        return error_response(code=404, error_message="Volunteering experience not found")

    header = await db.get(Header, volunteering.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    ai_suggestions = await generate_volunteering_description_from_ai(volunteering.role)

    return success_response(code=200, data={
        "message": "AI suggestions generated successfully",
        "suggestions": serialize_sqlalchemy_object(ai_suggestions)
    })


async def save_volunteering_description_service(volunteering_id: int, selected_description: str, user_id: int, db: AsyncSession):
    user_id = int(user_id)  
    volunteering = await db.get(VolunteeringExperience, volunteering_id)
    if not volunteering:
        return error_response(code=404, error_message="Volunteering experience not found")

    header = await db.get(Header, volunteering.header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized")

    volunteering.description = selected_description
    await db.commit()
    await db.refresh(volunteering)

    return success_response(code=200, data={
        "message": "Volunteering description updated successfully",
        "description": volunteering.description
    })
