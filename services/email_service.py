import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
from app.config import settings 

gmail_user = settings.get_secret(
    "gmail-app-user",
    settings.PROJECT_ID
)
gmail_password = settings.get_secret(
    "gmail-app-password",
    settings.PROJECT_ID
)



# -----------------------------
# Gmail SMTP configuration
# -----------------------------



def build_html_body(incident_number: str, incident_description: str) -> str:
    """Builds HTML email body."""

    html = f"""
    <html>
    <body style="font-family: Arial, Helvetica, sans-serif; line-height:1.5;">
        
        <h2 style="color:#b30000;">Incident Notification</h2>

        <p>An incident has been detected that requires attention.</p>

        <table style="border-collapse: collapse;">
            <tr>
                <td style="padding:6px; font-weight:bold;">Incident Number:</td>
                <td style="padding:6px;">{incident_number}</td>
            </tr>
            <tr>
                <td style="padding:6px; font-weight:bold;">Description:</td>
                <td style="padding:6px;">{incident_description}</td>
            </tr>
        </table>

        <p style="margin-top:20px;">
        This incident did <b>not match any known Knowledge Base articles</b>. 
        It may represent a new or emerging issue and should be reviewed with 
        appropriate priority.
        </p>

        <p>
        Please investigate and take necessary action.
        </p>

        <hr>

        <p style="font-size:12px;color:gray;">
        This is an automated notification from the AI Incident Monitoring System.
        </p>

    </body>
    </html>
    """

    return html


def send_email(
    recipients: List[str],
    incident_number: str,
    incident_description: str
) -> None:
    """Send incident notification email."""
    print("Sending Email..........")
    print(f"Gmail User: {gmail_user} ")
    print(f"Gmail password: {gmail_password} ")
    print(f"SMTP Server: {settings.EMAIL_SMTP_PORT}")
    print(f"SMTP Port: {settings.EMAIL_SMTP_PORT}")
    if not gmail_user or not gmail_password:
        raise ValueError("Missing Gmail credentials in environment variables")

    subject = f"⚠️ Incident Alert: {incident_number}"

    html_body = build_html_body(incident_number, incident_description)

    message = MIMEMultipart("alternative")
    message["From"] = gmail_user
    message["To"] = gmail_user #", ".join(recipients)
    message["Subject"] = subject

    message.attach(MIMEText(html_body, "html"))

    try:
        print("Connecting to Gmail SMTP server")

        with smtplib.SMTP(settings.EMAIL_SMTP_SERVER, settings.EMAIL_SMTP_PORT) as server:
            server.starttls()
            server.login(gmail_user, gmail_password)

            server.sendmail(
                from_addr=gmail_user,
                to_addrs=message["To"],
                msg=message.as_string()
            )

        print("Email sent successfully")

    except smtplib.SMTPException as e:
        print("Failed to send email")
        logging.exception(e)
        raise


# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":

    recipients = [
        "[email protected]",
        "[email protected]"
    ]

    send_email(
        recipients=recipients,
        incident_number="INC-10452",
        incident_description="AI monitoring detected abnormal API response latency."
    )