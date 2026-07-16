import random
import string
import resend
from datetime import datetime, timedelta, timezone

from backend.core.config import settings

resend.api_key = settings.resend_api_key

CODE_EXPIRE_MINUTES = 10


def generate_code() -> str:
    return "".join(random.choices(string.digits, k=6))


def get_expires_at() -> datetime:
    return datetime.now(timezone.utc) + timedelta(minutes=CODE_EXPIRE_MINUTES)


async def send_verification_email(email: str, code: str) -> None:
    resend.Emails.send({
        "from": "DocMind <onboarding@resend.dev>",
        "to": email,
        "subject": "Код подтверждения — DocMind",
        "html": f"""
            <h2>Подтверждение регистрации</h2>
            <p>Ваш код подтверждения:</p>
            <h1 style="letter-spacing: 8px; color: #4f7fff;">{code}</h1>
            <p>Код действителен {CODE_EXPIRE_MINUTES} минут.</p>
            <p>Если вы не регистрировались — просто проигнорируйте это письмо.</p>
        """,
    })