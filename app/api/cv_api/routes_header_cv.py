from fastapi import APIRouter, Depends, status , Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.dependencies import get_db
from app.database.models import Header
from app.schemas.cv import HeaderRequest
from app.utils.response_schemas import error_response, success_response, serialize_sqlalchemy_object
from app.api.auth_api.auth.routes_auth import get_current_user


router = APIRouter() 

async def enforce_json_content_type(request: Request):
    if not request.headers.get("content-type", "").startswith("application/json"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Unsupported Media Type. Content-Type must be application/json."
        )

@router.post("/api/headers/", tags=["Personal Information"], dependencies=[Depends(enforce_json_content_type)])
async def create_header(
    request: HeaderRequest, 
    user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    try:
        result = await db.execute(
            select(Header).where(Header.user_id == int(user["user_id"]))
        )
        existing_header = result.scalar_one_or_none()
        if existing_header:
            return error_response(
                code=status.HTTP_400_BAD_REQUEST,
                error_message="Header already exists for this user"
            )

        header = Header(user_id=int(user["user_id"]), **request.dict())
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

@router.get("/api/headers/{header_id}/", tags=["Personal Information"])
async def get_header(
    header_id: int, 
    user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):

    header = await db.get(Header, header_id)
    
    if not header or header.user_id != int(user["user_id"]):  
        return error_response(code=403, error_message="Unauthorized access to header")

    return success_response(code=200, data={"header":serialize_sqlalchemy_object(header)})


@router.put("/api/headers/{header_id}/", tags=["Personal Information"])
async def update_header(
    header_id: int, 
    request: HeaderRequest, 
    user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    header = await db.get(Header, header_id)
    if not header or header.user_id != int(user["user_id"]):  
        return error_response(code=403, error_message="Unauthorized access to header")

    for key, value in request.dict(exclude_unset=True).items():
        setattr(header, key, value)

    await db.commit()
    await db.refresh(header)
    return success_response(code=200, data={"message": "Header updated successfully", "header":serialize_sqlalchemy_object(header)})

@router.delete("/api/headers/{header_id}/", tags=["Personal Information"])
async def delete_header(
    header_id: int, 
    user: dict = Depends(get_current_user), 
    db: AsyncSession = Depends(get_db)
):
    header = await db.get(Header, header_id)
    
    if not header or header.user_id != int(user["user_id"]):  
        return error_response(code=403, error_message="Unauthorized access to header")

    await db.delete(header)
    await db.commit()
    
    return success_response(code=200, data={"message": "Header deleted successfully"})
