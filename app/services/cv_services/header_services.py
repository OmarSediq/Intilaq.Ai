from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models.cv_section_models import Header
from app.schemas.cv import HeaderRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from fastapi import status


async def create_header_service(request: HeaderRequest, user_id: int, db: AsyncSession):
    try:
        result = await db.execute(select(Header).where(Header.user_id == user_id))
        existing_header = result.scalar_one_or_none()
        if existing_header:
            return error_response(
                code=status.HTTP_400_BAD_REQUEST,
                error_message="Header already exists for this user"
            )

        header = Header(user_id=user_id, **request.dict())
        db.add(header)
        await db.commit()
        await db.refresh(header)

        return success_response(
            code=status.HTTP_201_CREATED,
            data={
                "message": "Header created successfully",
                "header": serialize_sqlalchemy_object(header)
            }
        )
    except Exception as e:
        print(f"[ERROR] Failed to create header: {e}")
        return error_response(
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_message="Internal error while creating header"
        )


async def get_header_service(header_id: int, user_id: int, db: AsyncSession):
    header = await db.get(Header, header_id)

    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized access to header")

    return success_response(code=200, data={"header": serialize_sqlalchemy_object(header)})


async def update_header_service(header_id: int, request: HeaderRequest, user_id: int, db: AsyncSession):
    header = await db.get(Header, header_id)
    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized access to header")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(header, key, value)

    await db.commit()
    await db.refresh(header)
    return success_response(code=200, data={
        "message": "Header updated successfully",
        "header": serialize_sqlalchemy_object(header)
    })


async def delete_header_service(header_id: int, user_id: int, db: AsyncSession):
    header = await db.get(Header, header_id)

    if not header or header.user_id != user_id:
        return error_response(code=403, error_message="Unauthorized access to header")

    await db.delete(header)
    await db.commit()
    return success_response(code=200, data={"message": "Header deleted successfully"})
