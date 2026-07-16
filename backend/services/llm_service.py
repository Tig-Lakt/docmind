from openai import AsyncOpenAI
from backend.core.config import settings
from backend.core.prompts import SYSTEM_PROMPT, USER_PROMPT
from backend.services.qdrant_service import search


openai = AsyncOpenAI(api_key=settings.openai_api_key)


async def ask_document(collection_name: str, question: str) -> dict:
    chunks = await search(collection_name, question, top_k=5)

    if not chunks:
        return {
            "answer": "В предоставленном документе ответ не найден.",
            "chunks_found": 0,
        }

    context = "\n\n---\n\n".join(chunks)

    system = SYSTEM_PROMPT.format(context=context)
    user = USER_PROMPT.format(question=question)

    response = await openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0,  
        max_tokens=1000,
    )

    return {
        "answer": response.choices[0].message.content,
        "chunks_found": len(chunks),
    }