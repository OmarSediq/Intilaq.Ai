from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.dependencies import get_db
from app.api.routes_auth import get_current_user
from app.database.models import Header, Education
from app.schemas.cv import EducationRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object
from sqlalchemy.future import select


router = APIRouter()


@router.post("/api/educations/", tags=["Education Management"])
async def create_education(
    request: EducationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
    header = result.scalars().first()
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


@router.get("/api/educations/{education_id}/", tags=["Education Management"])
async def get_education(
    education_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this education")

    return success_response(code=200, data={"education": serialize_sqlalchemy_object(education)})


@router.put("/api/educations/{education_id}/", tags=["Education Management"])
async def update_education(
    education_id: int,
    request: EducationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this education")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(education, key, value)

    await db.commit()
    await db.refresh(education)

    return success_response(code=200, data={
        "message": "Education updated successfully",
        "education": serialize_sqlalchemy_object(education)
    })


@router.delete("/api/educations/{education_id}/", tags=["Education Management"])
async def delete_education(
    education_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    education = await db.get(Education, education_id)
    if not education:
        return error_response(code=404, error_message="Education not found")

    header = await db.get(Header, education.header_id)
    if not header or header.user_id != int(user["user_id"]):
        return error_response(code=403, error_message="Unauthorized access to this education")

    await db.delete(education)
    await db.commit()
    return success_response(code=200, data={"message": "Education deleted successfully"})
