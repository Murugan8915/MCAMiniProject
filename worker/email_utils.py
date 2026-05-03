import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# MailHog SMTP settings
SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", 1025))

def send_email(to_email, subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = "recruitment@company.com"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}: {subject}")
        return True
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")
        return False

def send_shortlisted_email(to_email, candidate_name, job_title):
    subject = f"Congratulations! You are shortlisted for {job_title}"
    body = f"Hi {candidate_name},\n\nYou are shortlisted for the position of {job_title}. Please wait for the technical assignment notification.\n\nBest Regards,\nHR Team"
    return send_email(to_email, subject, body)

def send_rejected_email(to_email, candidate_name, job_title):
    subject = f"Update regarding your application for {job_title}"
    body = f"Hi {candidate_name},\n\nThank you for applying for the position of {job_title}. Unfortunately, we are not moving forward with your application at this time.\n\nBest Regards,\nHR Team"
    return send_email(to_email, subject, body)
