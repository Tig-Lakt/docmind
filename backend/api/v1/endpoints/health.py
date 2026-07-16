from fastapi import APIRouter, Depends, HTTPException
from backend.api.deps import get_session
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text


router = APIRouter(tags=["health"])


@router.get("/health", status_code=200)
async def health_check(session: AsyncSession=Depends(get_session)):
    try:
        stmp=text("SELECT 1")
        await session.execute(stmp)
        return {"status": "healthy", "message": "Service is running"}
    except SQLAlchemyError as e:
        raise HTTPException(status_code=503, detail="Database is unavailable")