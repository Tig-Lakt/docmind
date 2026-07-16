from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.schemas.schemas import UserLogin, Token
from backend.services.auth_service import AuthService
from backend.api.deps import get_auth_service

from backend.api.deps import get_templates


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="login.html")


@router.post("/login", response_model=Token)
async def login(
    user_data: UserLogin,
    service: AuthService = Depends(get_auth_service),
):
    return await service.login(user_data.email, user_data.password)


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="dashboard.html")