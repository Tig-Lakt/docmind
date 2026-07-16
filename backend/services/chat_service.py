from fastapi import HTTPException, status
from backend.repositories.document_repo import DocumentRepository
from backend.services.llm_service import ask_document


class ChatService:
    def __init__(self, repo: DocumentRepository):
        self.repo = repo

    async def ask(self, doc_id: int, user_id: int, question: str) -> dict:
        doc = await self.repo.get_by_id_and_user(doc_id, user_id)
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Документ не найден",
            )
        return await ask_document(doc.qdrant_collection, question)