import logging
import random
from datetime import datetime
from passlib.context import CryptContext
from email.message import EmailMessage
import ssl
import smtplib
from typing import TYPE_CHECKING, Optional, Any
from sqlalchemy.orm import Session
from config import settings

if TYPE_CHECKING:
    from sqlalchemy.orm import Session as SessionType
    from models import User


pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")


logging.basicConfig(level=logging.INFO)

emailSender = settings.email_sender
emailPassword = settings.email_password

def hash(password: str):
    return pwdContext.hash(password)

def verify(plainPassword, hashedPassword):
    return pwdContext.verify(plainPassword, hashedPassword)

def createUserName(name: str):
    name = name.lower()
    name = name.split(" ")
    if len(name) == 1:
        userName = name[0] + str(random.randint(0, 9999))
    else:
        userName = name[0] + name[1] + str(random.randint(0, 9999))
    return userName

def sendEmail(subject: str, body: str, receiver_email: str):
    em = EmailMessage()
    em['From'] = emailSender
    em['To'] = receiver_email
    em['Subject'] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(emailSender, emailPassword)
        smtp.sendmail(emailSender, receiver_email, em.as_string())

def get_user_by_email(db: 'SessionType', email: str) -> Optional[Any]:
    """
    Get a user by email from the database
    """
    from models import User  # Import here to avoid circular imports
    return db.query(User).filter(User.email == email).first()
