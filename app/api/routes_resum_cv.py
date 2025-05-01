from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from app.api.routes_auth import get_current_user
from app.core.dependencies import get_db
from app.services.mongo_services import get_mongo_client
from app.core.config import env
from app.utils.response_schemas import error_response 
from app.database.db_services import get_user_by_header_id, generate_docx_from_html
from motor.motor_asyncio import AsyncIOMotorClient
from app.database.models import Header
from sqlalchemy.future import select
import pdfkit
import io
from bson import ObjectId
from datetime import datetime
from io import BytesIO


router = APIRouter()

config = pdfkit.configuration(wkhtmltopdf="/usr/bin/wkhtmltopdf")

def safe_get(data, key, default=""):
    return data.get(key, default) if data.get(key) is not None else default

async def get_header_id_for_user(user_id: int, db: AsyncSession):
    result = await db.execute(select(Header.id).where(Header.user_id == user_id))
    header = result.scalar()
    return header

@router.get("/api/generate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def generate_cv(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_id = int(user["user_id"])
        header_id = await get_header_id_for_user(user_id, db)

        if not header_id:
            return error_response(code=404, error_message="Header not found")

        user_data = await get_user_by_header_id(db, header_id)

        if not user_data or user_data["user_id"] != user_id:
            return error_response(code=403, error_message="You do not have permission")

        template = env.get_template("resume_template.html")
        html_content = template.render(
            full_name=safe_get(user_data, "full_name"),
            job_title=safe_get(user_data, "job_title"),
            email=safe_get(user_data, "email"),
            phone_number=safe_get(user_data, "phone_number"),
            address=safe_get(user_data, "address"),
            years_of_experience=safe_get(user_data, "years_of_experience"),
            github_profile=safe_get(user_data, "github_profile"),
            linkedin_profile=safe_get(user_data, "linkedin_profile"),
            objective=safe_get(user_data, "objective"),
            education=safe_get(user_data, "education", []),
            experience=safe_get(user_data, "experience", []),
            technical_skills=safe_get(user_data, "technical_skills", []),
            languages=safe_get(user_data, "languages", []),
            certifications=safe_get(user_data, "certifications", []),
            projects=safe_get(user_data, "projects", []),
            volunteering_experience=safe_get(user_data, "volunteering_experience", []),
            awards=safe_get(user_data, "awards", [])
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        return error_response(code=500, error_message=f"Template rendering error: {str(e)}")

@router.get("/api/download-cv/pdf/", tags=["CV Exporting"])
async def download_and_store_cv_pdf(
    user: dict = Depends(get_current_user),
    db_sql: AsyncSession = Depends(get_db),
    mongo_client: AsyncIOMotorClient = Depends(get_mongo_client)
):
    try:
        user_id = int(user["user_id"])
        header_id = await get_header_id_for_user(user_id, db_sql)

        if not header_id:
            return error_response(code=404, error_message="Header not found")

        user_data = await get_user_by_header_id(db_sql, header_id)

        template = env.get_template("resume_template.html")
        html_content = template.render(**user_data)

        pdf_bytes = pdfkit.from_string(html_content, False, options={
            "page-size": "A4", "margin-top": "10mm", "margin-right": "10mm",
            "margin-bottom": "10mm", "margin-left": "10mm", "encoding": "UTF-8",
            "dpi": 300, "enable-local-file-access": None
        }, configuration=config)

        mongo_db = mongo_client["resumes_db"]
        fs = AsyncIOMotorGridFSBucket(mongo_db)

        metadata = {
            "user_id": user_id,
            "resume_name": user_data.get("full_name", "Generated_CV"),
            "uploaded_at": datetime.utcnow()
        }

        file_id = await fs.upload_from_stream(
            f"{metadata['resume_name']}.pdf",
            BytesIO(pdf_bytes),
            metadata=metadata
        )

        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={metadata['resume_name']}.pdf",
                "X-File-ID": str(file_id)
            }
        )

    except Exception as e:
        return error_response(code=500, error_message=f"PDF generation error: {str(e)}")

@router.get("/api/download-cv/docx/", tags=["CV Exporting"])
async def download_cv_docx(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_id = int(user["user_id"])
        header_id = await get_header_id_for_user(user_id, db)

        if not header_id:
            return error_response(code=404, error_message="Header not found")

        user_data = await get_user_by_header_id(db, header_id)

        template = env.get_template("resume_template.html")
        html_content = template.render(**user_data)

        docx_buffer = await generate_docx_from_html(html_content)

        return StreamingResponse(
            docx_buffer,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": f"attachment; filename={user_data.get('full_name', 'Generated_CV')}.docx"}
        )

    except Exception as e:
        return error_response(code=500, error_message=f"Template rendering error: {str(e)}")

@router.get("/api/regenerate-cv/", response_class=HTMLResponse, tags=["CV Exporting"])
async def regenerate_cv(
    user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        user_id = int(user["user_id"])
        header_id = await get_header_id_for_user(user_id, db)

        if not header_id:
            return error_response(code=404, error_message="Header not found")

        user_data = await get_user_by_header_id(db, header_id)

        template = env.get_template("resume_template.html")
        html_content = template.render(
            full_name=safe_get(user_data, "full_name"),
            job_title=safe_get(user_data, "job_title"),
            email=safe_get(user_data, "email"),
            phone_number=safe_get(user_data, "phone_number"),
            address=safe_get(user_data, "address"),
            years_of_experience=safe_get(user_data, "years_of_experience"),
            github_profile=safe_get(user_data, "github_profile"),
            linkedin_profile=safe_get(user_data, "linkedin_profile"),
            objective=safe_get(user_data, "objective"),
            education=safe_get(user_data, "education", []),
            experience=safe_get(user_data, "experience", []),
            technical_skills=safe_get(user_data, "technical_skills", []),
            languages=safe_get(user_data, "languages", []),
            certifications=safe_get(user_data, "certifications", []),
            projects=safe_get(user_data, "projects", []),
            volunteering_experience=safe_get(user_data, "volunteering_experience", []),
            awards=safe_get(user_data, "awards", [])
        )

        return HTMLResponse(content=html_content)

    except Exception as e:
        return error_response(code=500, error_message=f"Template rendering error: {str(e)}")

    
@router.get("/api/resumes/{file_id}/download", tags=["My Resume"])
async def download_resume_from_mongo(
    file_id: str,
    user=Depends(get_current_user),
    db=Depends(get_mongo_client)
):
    try:
        mongo_db = db["resumes_db"]
        file_doc = await mongo_db["fs.files"].find_one({"_id": ObjectId(file_id)})

        if not file_doc:
            return error_response(code=404, error_message="File not found")

        user_id_from_file = str(file_doc.get("metadata", {}).get("user_id"))
        if user_id_from_file != str(user["user_id"]):
            return error_response(code=403, error_message="You do not have access to this file")

        
       
        fs = AsyncIOMotorGridFSBucket(mongo_db)
        stream = await fs.open_download_stream(ObjectId(file_id))
        content = await stream.read()

        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={file_doc.get('filename', 'cv')}.pdf"}
        )

    except Exception as e:
        return error_response(code=500, error_message=f"Error fetching resume: {str(e)}")

