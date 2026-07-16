from typing import Annotated
from jose import jwt, JWTError
from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio.session import AsyncSession

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates

from backend.repositories.user_repo import UserRepository
from backend.repositories.password_reset_repo import PasswordResetRepository
from backend.core.config import settings
from backend.services.auth_service import AuthService
from backend.repositories.document_repo import DocumentRepository
from backend.services.document_service import DocumentService
from backend.db.database import AsyncSessionLocal

from backend.services.email_recovery_service import EmailRecoveryService#, get_recovery_service

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_auth_service(db: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(UserRepository(db))


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_session),
):
    from backend.repositories.user_repo import UserRepository
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный токен",
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    repo = UserRepository(db)
    user = await repo.get_by_id(int(user_id))
    if user is None:
        raise credentials_exception
    return user


def get_templates():
    return Jinja2Templates(directory="frontend/templates")


def get_document_service(db: AsyncSession = Depends(get_session)) -> DocumentService:
    return DocumentService(DocumentRepository(db))


async def get_recovery_service(db: AsyncSession = Depends(get_session)):
    user_repo = UserRepository(db)
    reset_repo = PasswordResetRepository(db)
    return EmailRecoveryService(user_repo, reset_repo)


EmailRecoveryServiceDep = Annotated[EmailRecoveryService, Depends(get_recovery_service)]