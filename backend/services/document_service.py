from fastapi import HTTPException, UploadFile, status
from backend.repositories.document_repo import DocumentRepository
from backend.services.file_storage import save_file_content
from backend.services.document_processor import extract_text, extract_text_from_url, split_text
from backend.services.qdrant_service import index_document

from backend.core.constants import ALLOWED_TYPES, MAX_FILE_SIZE


class DocumentService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def upload_file(self, file: UploadFile, user_id: int):
        ext = file.filename.rsplit(".", 1)[-1].lower()
        if ext not in ALLOWED_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Неподдерживаемый тип файла. Разрешены: {', '.join(ALLOWED_TYPES)}",
            )

        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="Файл слишком большой. Максимальный размер — 50 МБ",
            )

        file_path, filename = await save_file_content(content, user_id, file.filename)
        text = extract_text(file_path, ext)
        chunks = split_text(text)
        collection_name = f"user_{user_id}_doc_{filename}"
        await index_document(collection_name, chunks)
        return await self.repo.create(user_id, filename, file_path, ext, collection_name)

    async def upload_url(self, url: str, user_id: int):
        text = await extract_text_from_url(url)
        chunks = split_text(text)
        collection_name = f"user_{user_id}_url_{hash(url)}"
        await index_document(collection_name, chunks)
        return await self.repo.create(user_id, url, url, "url", collection_name)

    async def get_user_documents(self, user_id: int):
        return await self.repo.get_all_by_user(user_id)