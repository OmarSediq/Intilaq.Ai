import uuid
from datetime import datetime, timezone
from app.utils.response_schemas import success_response, error_response
from app.services.mongo_services import get_mongo_client  
from app.services.ai_services import generate_questions_using_gemini_hr
from app.schemas.hr_schemas.create_hr_interview import HRAddQuestionRequest
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
import smtplib
from app.core.config import settings
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text

TEMPLATES_DIR = "/app/templates"
env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))


async def create_hr_interview_metadata(request, hr_id):
    try:
        client = await get_mongo_client()
        db = client["hr_db"]
        interviews_col = db["hr_interviews"]
        questions_col = db["hr_interview_questions"]

        # Generate Interview Token
        interview_token = uuid.uuid4().hex

        # Save metadata
        interview_data = {
            "interview_token": interview_token,
            "job_title": request.job_title,
            "level": request.level,
            "job_requirements": request.job_requirements,
            "specific_date": request.specific_date,
            "date_range": request.date_range,
            "time": request.time,
            "hr_id": hr_id,
            "created_at": datetime.now(timezone.utc)
        }

        await interviews_col.insert_one(interview_data)

        # Generate Questions from Gemini
        ai_questions_raw = await generate_questions_using_gemini_hr(
            job_name=request.job_title,
            job_level=request.level,
            job_requirements=request.job_requirements or ""
        )
        questions = [q.strip() for q in ai_questions_raw.split("\n") if q.strip()]

        # Create one document with array of questions
        question_doc = {
            "interview_token": interview_token,
            "hr_id": hr_id,
            "questions": [
                {
                    "index": i + 1,
                    "text": q,
                    "response_type": "text",
                    "time_limit": None
                }
                for i, q in enumerate(questions)
            ],
            "created_at": datetime.now(timezone.utc)
        }

        await questions_col.insert_one(question_doc)

        return success_response(code=201, data={
            "message": "Interview metadata and AI questions created successfully.",
            "interview_token": interview_token,
            "ai_questions": [f"{i+1}. {q}" for i, q in enumerate(questions)]
        })


    except Exception as e:
        return error_response(code=500, error_message=f"Error saving interview: {str(e)}")
    
    
async def update_interview_question_by_index(interview_token: str, index: int, update_data: HRAddQuestionRequest):
    try:
        client = await get_mongo_client()
        db = client["hr_db"]
        questions_col = db["hr_interview_questions"]
        document = await questions_col.find_one({"interview_token": interview_token})
        if not document:
            return error_response(code=404, error_message="Interview not found.")

        questions = document.get("questions", [])
        if index < 0 or index >= len(questions):
            return error_response(code=404, error_message="Question index out of range.")
        questions[index] = {
            "index": index,
            "text": update_data.question_text,
            "response_type": update_data.response_type,
            "time_limit": update_data.time_limit,
        }
        await questions_col.update_one(
            {"interview_token": interview_token},
            {"$set": {f"questions.{index}": questions[index]}}
        )

        return success_response(code=200, data=questions[index])

    except Exception as e:
        return error_response(code=500, error_message=f"Error updating question: {str(e)}")


def extract_name_from_email(email: str) -> str:
    return email.split('@')[0].capitalize()

async def get_company_field_by_hr_id(hr_id: int, db: AsyncSession) -> str:
    query = text("SELECT company_field FROM hr_section.hr_users WHERE id = :hr_id")
    result = await db.execute(query, {"hr_id": hr_id})
    return result.scalar_one_or_none() or "your company"


def render_email_template(candidate_name: str, job_title: str, interview_date: str, interview_link: str, company_field: str) -> str:
    template = env.get_template("interview_invitation.html")
    return template.render(
        candidate_name=candidate_name,
        job_title=job_title,
        interview_date=interview_date,
        interview_link=interview_link,
        company_field=company_field
    )


async def send_and_save_invitations(
    interview_token: str,
    emails: list,
    email_description: str | None,
    interview_link: str,
    db: AsyncSession
):
    try:
        client = await get_mongo_client()
        mongo_db = client["hr_db"]
        collection = mongo_db["hr_interviews"]

        doc = await collection.find_one({"interview_token": interview_token})
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        job_title = doc.get("job_title", "Unknown")

        
        raw_date = doc.get("specific_date", doc.get("date_range", "Not Set"))
        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
            interview_date = parsed_date
        except Exception:
            interview_date = raw_date

        hr_id = doc.get("hr_id")

        company_field = await get_company_field_by_hr_id(hr_id, db)

        await collection.update_one(
            {"interview_token": interview_token},
            {"$set": {
                "candidate_emails": emails,
                "email_description": email_description,
                "interview_link": interview_link,
                 "company_field": company_field 
            }}
        )

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)

            for email in emails:
                candidate_name = extract_name_from_email(email)
                html_body = render_email_template(
                    candidate_name=candidate_name,
                    job_title=job_title,
                    interview_date=interview_date,
                    interview_link=interview_link,
                    company_field=company_field
                )
                msg = MIMEText(html_body, "html")
                msg["Subject"] = f"Interview Invitation - {job_title}"
                msg["From"] = settings.EMAIL_FROM
                msg["To"] = email
                server.sendmail(settings.EMAIL_FROM, email, msg.as_string())
                print(f"Email sent to {email}")

        return success_response(code=200, data={"message": "Emails sent and saved successfully."})

    except smtplib.SMTPException as e:
        return error_response(code=500, error_message=f"SMTP error: {str(e)}")
    except Exception as e:
        return error_response(code=500, error_message=f"Error occurred: {str(e)}")
