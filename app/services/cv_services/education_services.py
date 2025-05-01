from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import Header, Education
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object

async def get_user_header(user_id: int, db: AsyncSession):
    result = await db.execute(select(Header).where(Header.user_id == int(user_id)))
    return result.scalars().first()

async def create_education_service(request, user_id: int, db: AsyncSession):
    header = await get_user_header(user_id, db)
    if not header:
        return error_response(code=404, error_message="Header not found for this user.")

    education = Education(**request.dict(exclude={"header_id"}), header_id=header.id)
    db.add(education)
    await db.commit()
    await db.refresh(education)

    return success_response(code=201, data={
        "message": "Education created successfully",
        "education": serialize_sqlalchemy_object(education)
    })


async def get_education_service(education_id: int, user_id: int, db: AsyncSession):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this education")

    return success_response(code=200, data={"education": serialize_sqlalchemy_object(education)})


async def update_education_service(education_id: int, request, user_id: int, db: AsyncSession):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this education")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(education, key, value)

    await db.commit()
    await db.refresh(education)

    return success_response(code=200, data={
        "message": "Education updated successfully",
        "education": serialize_sqlalchemy_object(education)
    })


async def delete_education_service(education_id: int, user_id: int, db: AsyncSession):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or int(header.user_id) != int(user_id):
        return error_response(code=403, error_message="Unauthorized access to this education")

    await db.delete(education)
    await db.commit()

    return success_response(code=200, data={"message": "Education deleted successfully"})
