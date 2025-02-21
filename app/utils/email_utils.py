from app.config import settings  
import smtplib
from email.mime.text import MIMEText

def send_email(to_email: str, subject: str, body: str):
    """
    Sends an email using SMTP settings defined in the application configuration.

    Args:
        to_email (str): Recipient's email address.
        subject (str): Subject of the email.
        body (str): Body of the email.

    Returns:
        None
    """
    try:
        smtp_server = settings.SMTP_SERVER
        smtp_port = settings.SMTP_PORT
        from_email = settings.EMAIL_FROM
        password = settings.SMTP_PASSWORD
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = from_email
        msg["To"] = to_email

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  
            server.login(from_email, password)  
            server.sendmail(from_email, to_email, msg.as_string())
        print("Email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
    except Exception as e:
        print(f"Failed to send email: {e}")
