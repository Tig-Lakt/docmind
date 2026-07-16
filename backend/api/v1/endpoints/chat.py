from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.api.deps import get_session
from backend.models.document import Document
from backend.schemas.schemas import ChatRequest, ChatResponse
from backend.models.user import User
from backend.api.deps import get_current_user
from backend.services.llm_service import ask_document


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/ask", response_model=ChatResponse)
async def ask(
    body: ChatRequest,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Document).where(
            Document.doc_id == body.doc_id,
            Document.user_id == current_user.id,
        )
    )
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Документ не найден",
        )

    response = await ask_document(doc.qdrant_collection, body.question)
    return ChatResponse(**response)