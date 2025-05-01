from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.database.models import Header, Certifications
from app.schemas.cv import CertificationRequest, CertificationUpdateRequest
from app.utils.response_schemas import success_response, error_response, serialize_sqlalchemy_object

router = APIRouter()

@router.post("/api/certifications/", tags=["Projects & Certifications"])
async def create_certification(
    request: CertificationRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(select(Header).where(Header.user_id == int(user["user_id"])))
        header = result.scalars().first()

        if not header:
            return error_response(code=404, error_message="Header not found for this user.")

        certification = Certifications(
            **request.dict(exclude={"header_id"}),
            header_id=header.id
        )

        db.add(certification)
        await db.commit()
        await db.refresh(certification)

        return success_response(
            code=201,
            data={
                "message": "Certification created successfully",
                "data": serialize_sqlalchemy_object(certification)
            }
        )

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.get("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
async def get_certification(
    certification_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        certification = await db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await db.get(Header, certification.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to view this certification.")

        return success_response(code=200, data={"data": serialize_sqlalchemy_object(certification)})

    except Exception as e:
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.put("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
async def update_certification(
    certification_id: int,
    request: CertificationUpdateRequest,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        certification = await db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await db.get(Header, certification.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to update this certification.")

        update_data = request.dict(exclude_unset=True)
        if "link" in update_data and update_data["link"] is not None:
            update_data["link"] = str(update_data["link"])

        for key, value in update_data.items():
            setattr(certification, key, value)

        await db.commit()
        await db.refresh(certification)

        return success_response(code=200, data={
            "message": "Certification updated successfully",
            "data": serialize_sqlalchemy_object(certification)
        })

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))


@router.delete("/api/certifications/{certification_id}/", tags=["Projects & Certifications"])
async def delete_certification(
    certification_id: int,
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        certification = await db.get(Certifications, certification_id)
        if not certification:
            return error_response(code=404, error_message="Certification not found")

        header = await db.get(Header, certification.header_id)
        if not header or header.user_id != int(user["user_id"]):
            return error_response(code=403, error_message="You do not have permission to delete this certification.")

        await db.delete(certification)
        await db.commit()

        return success_response(code=200, data={"message": "Certification deleted successfully"})

    except Exception as e:
        await db.rollback()
        return error_response(code=500, error_message="Unexpected error occurred", data=str(e))
