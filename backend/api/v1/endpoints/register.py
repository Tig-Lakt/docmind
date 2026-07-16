from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.api.deps import get_session
from backend.repositories.user_repo import UserRepository
from backend.repositories.pending_repo import PendingRepository
from backend.services.email_service import generate_code, get_expires_at, send_verification_email
from backend.core.security import hash_password, create_access_token
from backend.schemas.schemas import UserCreate, RegisterInitResponse, ConfirmRegistration, ResendCode, Token
from datetime import datetime, timezone

from backend.api.deps import get_templates


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


def get_repos(db: AsyncSession = Depends(get_session)):
    return UserRepository(db), PendingRepository(db)


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="register.html")


@router.post("/register", response_model=RegisterInitResponse)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(db)
    pending_repo = PendingRepository(db)

    # Проверяем что email не занят
    existing = await user_repo.get_by_email(user_data.email)
    if existing and existing.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email уже зарегистрирован",
        )

    # Создаём неактивного пользователя если не существует
    if not existing:
        await user_repo.create(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            is_active=False,
        )

    # Генерируем и отправляем код
    code = generate_code()
    expires_at = get_expires_at()
    await pending_repo.create(user_data.email, code, expires_at)
    await send_verification_email(user_data.email, code)

    return RegisterInitResponse(message="Код подтверждения отправлен на email")


@router.post("/confirm-email", response_model=Token)
async def confirm_email(
    body: ConfirmRegistration,
    db: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(db)
    pending_repo = PendingRepository(db)

    verification = await pending_repo.get_latest_by_email(body.email)

    if not verification:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код не найден. Запросите новый.",
        )

    if verification.is_used:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код уже использован. Запросите новый.",
        )

    if datetime.now(timezone.utc) > verification.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Код истёк. Запросите новый.",
        )

    if verification.code != body.code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный код",
        )

    # Активируем пользователя
    user = await user_repo.get_by_email(body.email)
    await user_repo.activate(user.id)
    await pending_repo.mark_as_used(verification.id)

    token = create_access_token({"sub": str(user.id)})
    return Token(access_token=token)


@router.post("/resend-code", response_model=RegisterInitResponse)
async def resend_code(
    body: ResendCode,
    db: AsyncSession = Depends(get_session),
):
    user_repo = UserRepository(db)
    pending_repo = PendingRepository(db)

    user = await user_repo.get_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email не найден",
        )

    if user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Аккаунт уже активирован",
        )

    code = generate_code()
    expires_at = get_expires_at()
    await pending_repo.create(body.email, code, expires_at)
    await send_verification_email(body.email, code)

    return RegisterInitResponse(message="Новый код отправлен на email")


@router.get("/confirm-email", response_class=HTMLResponse)
async def confirm_email_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="confirm_email.html")