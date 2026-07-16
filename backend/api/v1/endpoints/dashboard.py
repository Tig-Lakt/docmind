from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

from backend.api.deps import get_templates


router = APIRouter(prefix="/api/v1/service", tags=["service"])


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request, templates: Jinja2Templates = Depends(get_templates)):
    return templates.TemplateResponse(request=request, name="dashboard.html")
