"""Email sending utilities for password reset."""
import logging
import resend

from ..config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(to_email: str, reset_link: str) -> None:
    """
    Send a password reset email via Resend.

    If RESEND_API_KEY is not configured, logs the reset link to the console
    instead (useful for development or before Resend is set up).
    """
    if not settings.RESEND_API_KEY:
        logger.info(
            f"[PASSWORD RESET] RESEND_API_KEY not set. Reset link for {to_email}:\n{reset_link}"
        )
        return

    resend.api_key = settings.RESEND_API_KEY

    text_body = (
        f"Hi,\n\n"
        f"Click the link below to reset your Golf Pick'em password:\n\n"
        f"{reset_link}\n\n"
        f"This link expires in 1 hour. If you didn't request this, you can ignore this email."
    )
    html_body = f"""
    <html>
    <body style="font-family: sans-serif; color: #333; max-width: 480px; margin: 0 auto; padding: 32px 16px;">
      <p style="font-size: 16px;">Hi,</p>
      <p style="font-size: 16px;">Click the button below to reset your <strong>Golf Pick&apos;em</strong> password:</p>
      <p style="margin: 32px 0;">
        <a href="{reset_link}"
           style="background:#1a5c38;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:600;font-size:15px;">
          Reset Password
        </a>
      </p>
      <p style="color:#888;font-size:12px;">
        Or copy this URL into your browser:<br>
        <a href="{reset_link}" style="color:#1a5c38;">{reset_link}</a>
      </p>
      <p style="color:#888;font-size:12px;">
        This link expires in 1 hour. If you didn&apos;t request this, you can ignore this email.
      </p>
    </body>
    </html>
    """

    resend.Emails.send({
        "from": settings.RESEND_FROM_EMAIL,
        "to": [to_email],
        "subject": "Reset your Golf Pick'em password",
        "html": html_body,
        "text": text_body,
    })
