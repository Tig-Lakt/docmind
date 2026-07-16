
from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from backend.schemas.schemas import PasswordResetConfirm, PasswordResetRequest

from backend.api.deps import get_templates, EmailRecoveryServiceDep


router = APIRouter(prefix="/api/v1/recovery", tags=["recovery"])


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED,)
async def request_password_reset(
    body: PasswordResetRequest,
    service: EmailRecoveryServiceDep,
) -> dict[str, str]:
    await service.request_reset(body.email)
    return {"message": "Если email зарегистрирован — письмо отправлено"}


@router.get("/reset-password", response_class=HTMLResponse)
async def reset_password_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="reset_password.html")


@router.post("/reset-password", status_code=status.HTTP_200_OK,)
async def reset_password(
    body: PasswordResetConfirm,
    service: EmailRecoveryServiceDep,
) -> dict[str, str]:
    await service.reset_password(body.token, body.new_password)
    return {"message": "Пароль успешно изменён"}


@router.get("/forgot-password", response_class=HTMLResponse)
async def register_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="email_recovery.html")
