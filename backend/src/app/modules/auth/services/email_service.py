from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import EmailStr, NameEmail, SecretStr
from src.app.core.config import settings
from src.app.core.logger import get_logger

logger = get_logger(__name__)

def plain_value(value):
    if isinstance(value, SecretStr):
        return value.get_secret_value()
    return value

def recipient(email: EmailStr) -> NameEmail:
    return NameEmail(
        name=str(email),
        email=str(email),
    )

conf = ConnectionConfig(
    MAIL_USERNAME=plain_value(settings.MAIL_USERNAME) or "test",
    MAIL_PASSWORD=SecretStr(plain_value(settings.MAIL_PASSWORD) or "test"),
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=bool(settings.MAIL_USERNAME and settings.MAIL_PASSWORD),
    VALIDATE_CERTS=False
)

fm = FastMail(conf)

async def send_activation_email(email_to: EmailStr, token: str):
    activation_link = f"{settings.FRONTEND_URL}/activate?token={token}"
    
    html_body = f"""
    <h3>Welcome to Annotio!</h3>
    <p>Thank you for registering. Click the link below to activate your account:</p>
    <p><a href="{activation_link}">{activation_link}</a></p>
    <br>
    <p>The link will expire in 24 hours.</p>
    """

    message = MessageSchema(
        subject="Activate your Annotio account",
        recipients=[recipient(email_to)],
        body=html_body,
        subtype=MessageType.html
    )
    
    try:
        await fm.send_message(message)
        logger.info("activation_email_sent_successfully", email=email_to)
    except Exception as e:
        logger.error("failed_to_send_activation_email", error=str(e), email=email_to)
        # Błąd logujemy, ale nie rzucamy HTTPException bo działa w BackgroundTasks
        # raise FailedToSentActivationEmailException()

async def send_password_reset_email(email_to: EmailStr, token: str):
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"

    html_body = f"""
    <h3>Reset your Annotio password</h3>
    <p>We received a request to reset the password for your account.</p>
    <p>Click the link below to reset it:</p>
    <p><a href="{reset_link}">{reset_link}</a></p>
    <br>
    <p>If this wasn't you, please ignore this message. The link will expire in one hour.</p>
    """

    message = MessageSchema(
        subject="Reset your Annotio password",
        recipients=[recipient(email_to)],
        body=html_body,
        subtype=MessageType.html
    )

    try:
        await fm.send_message(message)
        logger.info("password_reset_email_sent_successfully", email=email_to)
    except Exception as e:
        logger.error("failed_to_send_password_reset_email", error=str(e), email=email_to)
        # Błąd logujemy, ale nie rzucamy HTTPException bo działa w BackgroundTasks
        # raise FailedToSentPasswordResetEmailException()
