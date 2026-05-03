import smtplib
from email.mime.text import MIMEText

SMTP_HOST = "mailhog"
SMTP_PORT = 1025

def send_email(to_email: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "hr@recruitment.com"
    msg["To"] = to_email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")

def notify_shortlisted(to_email: str, job_title: str):
    subject = f"Congratulations! You've been shortlisted for {job_title}"
    body = f"Hello,\n\nWe are pleased to inform you that your profile has been shortlisted for the {job_title} role.\nYou will receive further instructions for the technical round shortly.\n\nBest Regards,\nHR Team"
    send_email(to_email, subject, body)

def notify_rejected(to_email: str, job_title: str):
    subject = f"Update regarding your application for {job_title}"
    body = f"Hello,\n\nThank you for applying for the {job_title} role. Unfortunately, we will not be moving forward with your application at this time.\n\nBest Regards,\nHR Team"
    send_email(to_email, subject, body)

def notify_selected(to_email: str, job_title: str):
    subject = f"Congratulations! You are Selected for {job_title}"
    body = f"Hello,\n\nWe are thrilled to inform you that you have been selected for the {job_title} role!\n\nPlease log in to the candidate portal to upload your Education and Experience documents to complete the onboarding process.\n\nBest Regards,\nHR Team"
    send_email(to_email, subject, body)
