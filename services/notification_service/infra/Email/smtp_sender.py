import asyncio
import smtplib
from email.mime.text import MIMEText
from Core.config import settings

class EmailSenderService:

    async def send_email(self, to_email: str, subject: str, html_body: str):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(
            None,
            self._send_sync,
            to_email,
            subject,
            html_body,
        )

    def _send_sync(self, to_email, subject, html_body):
        msg = MIMEText(html_body, "html")
        msg["Subject"] = subject
        msg["From"] = settings.EMAIL_FROM
        msg["To"] = to_email

        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.EMAIL_FROM, to_email, msg.as_string())
