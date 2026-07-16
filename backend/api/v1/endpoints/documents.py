from fastapi import APIRouter, Depends, UploadFile, File
from typing import Annotated

from backend.schemas.schemas import DocumentResponse
from backend.models.user import User
from backend.api.deps import get_current_user, get_document_service
from backend.services.document_service import DocumentService


router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: Annotated[UploadFile, File()],
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    return await service.upload_file(file, current_user.id)


@router.get("/my", response_model=list[DocumentResponse])
async def my_documents(
    service: DocumentService = Depends(get_document_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_user_documents(current_user.id)

