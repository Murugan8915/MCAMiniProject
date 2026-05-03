import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Configuration (MailHog defaults)
SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

def send_email(to_email: str, subject: str, body: str):
    try:
        msg = MIMEMultipart()
        msg['From'] = "recruit-ai@company.com"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))
        
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def notify_shortlist(to_email: str, job_title: str):
    subject = f"Shortlisted: {job_title}"
    body = f"Congratulations! You have been shortlisted for the position of {job_title}. Our technical panel will reach out soon."
    return send_email(to_email, subject, body)

def notify_rejection(to_email: str, job_title: str):
    subject = f"Application Status: {job_title}"
    body = f"Thank you for your interest in the {job_title} position. After reviewing your application, we have decided to move forward with other candidates."
    return send_email(to_email, subject, body)
