"""
Email sending utility for Bear's Den.
Supports SMTP or debug mode (logs instead of sending).

Configure via environment variables:
- EMAIL_MODE: 'smtp', 'debug' (default: debug)
- SMTP_HOST: SMTP server hostname
- SMTP_PORT: SMTP server port (default: 587)
- SMTP_USER: SMTP username
- SMTP_PASSWORD: SMTP password
- SMTP_FROM: From email address
- SMTP_FROM_NAME: From name (default: "Bear's Den")
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional

logger = logging.getLogger(__name__)

# Configuration from environment
EMAIL_MODE = os.getenv('EMAIL_MODE', 'debug')
SMTP_HOST = os.getenv('SMTP_HOST', '')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM = os.getenv('SMTP_FROM', 'noreply@bearsden.app')
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', "Bear's Den")


def send_email(to_email: str, subject: str, body_text: str, body_html: Optional[str] = None) -> tuple[bool, str]:
    """
    Send an email.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text body
        body_html: Optional HTML body

    Returns:
        (success, message) tuple
    """
    if EMAIL_MODE == 'debug':
        # Debug mode - log instead of sending
        logger.info(f"[EMAIL DEBUG] To: {to_email}")
        logger.info(f"[EMAIL DEBUG] Subject: {subject}")
        logger.info(f"[EMAIL DEBUG] Body: {body_text}")
        print(f"\n{'='*50}")
        print(f"EMAIL DEBUG MODE")
        print(f"{'='*50}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body_text}")
        print(f"{'='*50}\n")
        return True, "Email logged (debug mode)"

    if EMAIL_MODE == 'smtp':
        if not all([SMTP_HOST, SMTP_USER, SMTP_PASSWORD]):
            logger.error("SMTP not configured. Set SMTP_HOST, SMTP_USER, SMTP_PASSWORD")
            return False, "Email not configured"

        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_FROM}>"
            msg['To'] = to_email

            # Attach plain text
            msg.attach(MIMEText(body_text, 'plain'))

            # Attach HTML if provided
            if body_html:
                msg.attach(MIMEText(body_html, 'html'))

            # Send via SMTP
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.send_message(msg)

            logger.info(f"Email sent to {to_email}: {subject}")
            return True, "Email sent"

        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP authentication failed")
            return False, "Email authentication failed"
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {e}")
            return False, f"Email error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected email error: {e}")
            return False, f"Email error: {str(e)}"

    return False, f"Unknown email mode: {EMAIL_MODE}"


def send_verification_code(to_email: str, code: str) -> tuple[bool, str]:
    """
    Send email verification code.

    Args:
        to_email: Recipient email address
        code: 6-digit verification code

    Returns:
        (success, message) tuple
    """
    subject = "Bear's Den - Verify Your New Email"

    body_text = f"""Hi Chief!

You requested to change your email address to: {to_email}

Your verification code is: {code}

This code expires in 15 minutes.

If you didn't request this change, you can safely ignore this email.

- The Bear's Den Team
"""

    body_html = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; background: #0A1628; color: #E0F7FF; padding: 20px; }}
        .container {{ max-width: 500px; margin: 0 auto; background: #1A3A5C; padding: 30px; border-radius: 10px; }}
        .code {{ font-size: 32px; font-weight: bold; text-align: center; background: #0A1628; padding: 20px; border-radius: 8px; letter-spacing: 8px; color: #7DD3FC; margin: 20px 0; }}
        .footer {{ font-size: 12px; color: #93C5E0; margin-top: 30px; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #7DD3FC;">Verify Your New Email</h2>
        <p>Hi Chief!</p>
        <p>You requested to change your email address to: <strong>{to_email}</strong></p>
        <p>Your verification code is:</p>
        <div class="code">{code}</div>
        <p>This code expires in <strong>15 minutes</strong>.</p>
        <p>If you didn't request this change, you can safely ignore this email.</p>
        <div class="footer">
            - The Bear's Den Team<br>
            <a href="https://bearsden.app" style="color: #7DD3FC;">bearsden.app</a>
        </div>
    </div>
</body>
</html>
"""

    return send_email(to_email, subject, body_text, body_html)
