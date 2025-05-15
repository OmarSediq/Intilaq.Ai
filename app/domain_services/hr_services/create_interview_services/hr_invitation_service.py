from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from email.mime.text import MIMEText
import smtplib
from app.core.config import settings
from app.utils.response_schemas import success_response, error_response

class HRInvitationService:
    def __init__(self, mongo_client, db: AsyncSession):
        self.mongo = mongo_client["hr_db"]
        self.collection = self.mongo["hr_interviews"]
        self.db = db
        self.env = Environment(loader=FileSystemLoader("/app/templates"))

    async def get_company_field_by_hr_id(self, hr_id: int) -> str:
        query = text("SELECT company_field FROM hr_section.hr_users WHERE id = :hr_id")
        result = await self.db.execute(query, {"hr_id": hr_id})
        return result.scalar_one_or_none() or "your company"

    def extract_name_from_email(self, email: str) -> str:
        return email.split('@')[0].capitalize()

    def render_email_template(self, candidate_name, job_title, interview_date, interview_link, company_field):
        template = self.env.get_template("interview_invitation.html")
        return template.render(
            candidate_name=candidate_name,
            job_title=job_title,
            interview_date=interview_date,
            interview_link=interview_link,
            company_field=company_field
        )

    async def send_invitations(self, interview_token: str, emails: list, email_description: str, interview_link: str):
        doc = await self.collection.find_one({"interview_token": interview_token})
        if not doc:
            return error_response(code=404, error_message="Interview not found.")

        job_title = doc.get("job_title", "Unknown")
        raw_date = doc.get("specific_date", doc.get("date_range", "Not Set"))

        try:
            parsed_date = datetime.strptime(raw_date, "%Y-%m-%d")
        except Exception:
            parsed_date = raw_date

        hr_id = doc.get("hr_id")
        company_field = await self.get_company_field_by_hr_id(hr_id)

        await self.collection.update_one(
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
                name = self.extract_name_from_email(email)
                body = self.render_email_template(
                    candidate_name=name,
                    job_title=job_title,
                    interview_date=parsed_date,
                    interview_link=interview_link,
                    company_field=company_field
                )
                msg = MIMEText(body, "html")
                msg["Subject"] = f"Interview Invitation - {job_title}"
                msg["From"] = settings.EMAIL_FROM
                msg["To"] = email
                server.sendmail(settings.EMAIL_FROM, email, msg.as_string())

        return success_response(code=200, data={"message": "Emails sent and saved successfully."})
