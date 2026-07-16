import uuid
import resend
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from backend.core.config import settings
from backend.core.constants import TOKEN_EXPIRE_HOURS
from backend.core.security import hash_password
from backend.repositories.password_reset_repo import PasswordResetRepository
from backend.repositories.user_repo import UserRepository


resend.api_key = settings.resend_api_key


class EmailRecoveryService:
    def __init__(self, user_repo: UserRepository, reset_repo: PasswordResetRepository):
        self.user_repo = user_repo
        self.reset_repo = reset_repo

    async def request_reset(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            return

        token = uuid.uuid4().hex
        expires_at = datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRE_HOURS)
        await self.reset_repo.create(user.id, token, expires_at)

        reset_link = f"http://docmind.site/api/v1/recovery/reset-password?token={token}"
        await self._send_reset_email(to=email, reset_link=reset_link)

    async def reset_password(self, token: str, new_password: str) -> None:
        reset_token = await self.reset_repo.get_by_token(token)

        if not reset_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Недействительная ссылка",
            )
        if reset_token.is_used:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ссылка уже была использована",
            )
        if datetime.now(timezone.utc) > reset_token.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ссылка истекла. Запросите новую.",
            )

        await self.user_repo.update_password(
            reset_token.user_id, hash_password(new_password)
        )
        await self.reset_repo.mark_as_used(reset_token.id)

    async def _send_reset_email(self, to: str, reset_link: str) -> None:
        resend.Emails.send({
            "from": "DocMind <onboarding@resend.dev>",
            "to": to,
            "subject": "Восстановление пароля — DocMind",
            "html": f"""
                <h2>Восстановление пароля</h2>
                <p>Вы запросили сброс пароля. Перейдите по ссылке:</p>
                <a href="{reset_link}">Сбросить пароль</a>
                <p>Ссылка действительна 1 час.</p>
                <p>Если вы не запрашивали сброс — просто проигнорируйте это письмо.</p>
            """,
        })


