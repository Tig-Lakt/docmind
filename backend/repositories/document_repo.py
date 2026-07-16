from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.models.document import Document


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        user_id: int,
        filename: str,
        file_path: str,
        file_type: str,
        qdrant_collection: str,
    ) -> Document:
        doc = Document(
            user_id=user_id,
            filename=filename,
            file_path=file_path,
            file_type=file_type,
            qdrant_collection=qdrant_collection,
        )
        self.db.add(doc)
        await self.db.commit()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(Document.doc_id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_and_user(self, doc_id: int, user_id: int) -> Document | None:
        result = await self.db.execute(
            select(Document).where(
                Document.doc_id == doc_id,
                Document.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_all_by_user(self, user_id: int) -> list[Document]:
        result = await self.db.execute(
            select(Document).where(Document.user_id == user_id)
        )
        return result.scalars().all()