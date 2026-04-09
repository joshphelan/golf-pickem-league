"""Email sending utilities for password reset."""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """
    Send a password reset email.

    If SMTP is not configured, logs the reset link to console instead
    (useful for development or when email is not yet set up).
    """
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        logger.info(
            f"[PASSWORD RESET] SMTP not configured. Reset link for {to_email}:\n{reset_link}"
        )
        return

    from_email = settings.SMTP_FROM_EMAIL or settings.SMTP_USER

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Reset your Golf Pick'em password"
    msg["From"] = from_email
    msg["To"] = to_email

    text_body = (
        f"Hi,\n\n"
        f"Click the link below to reset your Golf Pick'em password:\n\n"
        f"{reset_link}\n\n"
        f"This link expires in 1 hour. If you didn't request this, you can ignore this email."
    )
    html_body = f"""
    <html>
    <body style="font-family: sans-serif; color: #333;">
      <p>Hi,</p>
      <p>Click the link below to reset your <strong>Golf Pick'em</strong> password:</p>
      <p style="margin: 24px 0;">
        <a href="{reset_link}"
           style="background:#1a5c38;color:#fff;padding:12px 24px;border-radius:6px;text-decoration:none;font-weight:600;">
          Reset Password
        </a>
      </p>
      <p style="color:#666;font-size:13px;">
        Or copy this URL: <a href="{reset_link}">{reset_link}</a>
      </p>
      <p style="color:#666;font-size:13px;">
        This link expires in 1 hour. If you didn't request this, you can ignore this email.
      </p>
    </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(from_email, to_email, msg.as_string())
