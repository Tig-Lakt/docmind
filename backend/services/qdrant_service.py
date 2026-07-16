from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from openai import AsyncOpenAI
from backend.core.config import settings
import uuid

qdrant = QdrantClient(url=settings.qdrant_url)
openai = AsyncOpenAI(api_key=settings.openai_api_key)

from backend.core.constants import VECTOR_SIZE


async def get_embedding(text: str) -> list[float]:
    response = await openai.embeddings.create(
        input=text,
        model="text-embedding-3-small",
    )
    return response.data[0].embedding


async def index_document(collection_name: str, chunks: list[str]) -> None:
    qdrant.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
    )
    points = []
    for i, chunk in enumerate(chunks):
        embedding = await get_embedding(chunk)
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={"text": chunk, "chunk_index": i},
        ))
    qdrant.upsert(collection_name=collection_name, points=points)


async def search(collection_name: str, query: str, top_k: int = 5) -> list[str]:
    embedding = await get_embedding(query)
    results = qdrant.query_points(
        collection_name=collection_name,
        query=embedding,
        limit=top_k,
    )
    return [r.payload["text"] for r in results.points]

