from datetime import datetime, timezone
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select
from backend.models.email_verification import EmailVerification


class PendingRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, email: str, code: str, expires_at: datetime) -> EmailVerification:
        verification = EmailVerification(
            email=email,
            code=code,
            expires_at=expires_at,
            created_at=datetime.now(timezone.utc),
        )
        self.db.add(verification)
        await self.db.commit()
        await self.db.refresh(verification)
        return verification

    async def get_latest_by_email(self, email: str) -> EmailVerification | None:
        result = await self.db.execute(
            select(EmailVerification)
            .where(EmailVerification.email == email)
            .order_by(EmailVerification.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def mark_as_used(self, verification_id: int) -> None:
        result = await self.db.execute(
            select(EmailVerification).where(EmailVerification.id == verification_id)
        )
        verification = result.scalar_one_or_none()
        if verification:
            verification.is_used = True
            await self.db.commit()