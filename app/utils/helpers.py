from fastapi import FastAPI, HTTPException, Depends, status, Request, UploadFile
from fastapi_jwt_auth2 import AuthJWT
from typing import List
from functools import wraps
import pytz
import datetime
from datetime import datetime, timedelta
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import uuid
import random
import mimetypes
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
# import shortuuid
import os
from sqlalchemy import text, select, and_, desc, func, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
import aiosmtplib
import io
from fastapi.templating import Jinja2Templates
from user_agents import parse
import math
# import fitz
from typing import Optional

from app.models.jwt_tokens import JwtToken


from app.config.main_config import Config


templates = Jinja2Templates(directory="app/templates")
    
def generate_jti() -> str:
    """
    Generate a unique JWT ID by combining a UUID with a random 6-digit number.
    """
    return str(uuid.uuid4()) + '-' + str(random.randint(100000, 999999))


def jwt_required_admin(refresh: bool = False):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            Authorize: AuthJWT = kwargs.get('Authorize')
            if not Authorize:
                raise HTTPException(status_code=400, detail="Authorize dependency is missing.")
            
            if refresh:
                Authorize.jwt_refresh_token_required()
            else:
                Authorize.jwt_required()
            # # Get and decrypt user type from JWT
            # user_type = Authorize.get_raw_jwt().get('user_type')
            # user_type = decrypt_text_non_async(user_type)  # Replace with your decryption function
            # # Validate user type
            # if user_type not in user_types:
            #     raise HTTPException(status_code=403, detail="Permission denied! Invalid user type.")
            
            # Call the original route function
            return await func(*args, **kwargs)
        return wrapper
    return decorator


async def is_token_revoked(jwt_header, jwt_payload, db: AsyncSession):
    try:
        jti = jwt_payload.get("jti")
        if not jti:
            return False

        # Use async query to check if token is blacklisted
        result = await db.execute(select(JwtToken).filter_by(access_jti=jti, revoked=True))
        token_entry = result.scalars().first()

        return bool(token_entry)
    except Exception as ex:
        print(f"Error checking JTI blacklist: {str(ex)}")
        return False


async def send_email_async(
    to,
    subject,
    body,
    display_name: Optional[str] = None,
    attachment: Optional[str] = None,
    attachment_filename="document.pdf",
    sender_email: Optional[str] = None,
    mail_host: Optional[str] = None,
    mail_port: Optional[int] = None,
    mail_username: Optional[str] = None,
    mail_password: Optional[str] = None,
):
    """
    Sends an email asynchronously using aiosmtplib.
    """

    smtp_sender_email = sender_email if sender_email is not None else Config.SMTP_SENDER_EMAIL
    smtp_host = mail_host if mail_host is not None else Config.SMTP_HOST
    smtp_port = int(mail_port if mail_port is not None else Config.SMTP_PORT)
    smtp_username = mail_username if mail_username is not None else Config.SMTP_USERNAME
    smtp_password = mail_password if mail_password is not None else Config.SMTP_PASSWORD
    from_name = (display_name if display_name is not None else Config.SMTP_SENDER_NAME).title()

    msg = MIMEMultipart()
    msg['From'] = f'{from_name.title()} <{smtp_sender_email}>'
    msg['To'] = to
    msg['Subject'] = subject
    # msg['Reply-To'] = Config.SMTP_REPLY_TO_EMAIL
    msg.attach(MIMEText(body, 'html'))

    if attachment:
        if isinstance(attachment, io.BytesIO):
            # attachment.seek(0)  # VERY IMPORTANT
            part = MIMEApplication(attachment.read(), _subtype="pdf")
            part.add_header("Content-Disposition", "attachment", filename=attachment_filename)
            msg.attach(part)
        elif isinstance(attachment, str) and os.path.isfile(attachment):
            print("File Attach..")
            content_type, encoding = mimetypes.guess_type(attachment)
            if content_type is None or encoding is not None:
                content_type = "application/octet-stream"
            main_type, sub_type = content_type.split("/", 1)

            with open(attachment, "rb") as file:
                part = MIMEApplication(file.read(), _subtype=sub_type)
                part.add_header("Content-Disposition", "attachment", filename=attachment_filename)
                msg.attach(part)
    try:
        # Create an SMTP client and send the email
        smtp_client = aiosmtplib.SMTP(
            hostname=smtp_host,
            port=int(smtp_port),
            start_tls=True
        )

        await smtp_client.connect()
        await smtp_client.login(smtp_username, smtp_password)
        await smtp_client.send_message(msg)
        await smtp_client.quit()

        print(f"✅ Email sent successfully to: {to}")
        return True
    except Exception as e:
        print(f"❌ Error sending email: {e}")
        return False
    

def get_cuurent_datetime() -> str:
    """
    Returns current datetime in Asia/Kolkata timezone
    formatted as 'YYYY-MM-DD HH:MM:SS.microseconds+05:30'.
    """
    tz = pytz.timezone(Config.TIME_ZONE)
    now = datetime.now(tz)
    formatted = now.strftime("%Y-%m-%d %H:%M:%S.%f%z")
    # Insert colon in timezone offset to match +05:30
    return now