import os
import uuid
from fastapi import UploadFile

from backend.core.constants import UPLOAD_DIR


def get_upload_path(user_id: int, filename: str) -> str:
    user_dir = os.path.join(UPLOAD_DIR, str(user_id))
    os.makedirs(user_dir, exist_ok=True)
    unique_name = f"{uuid.uuid4().hex}_{filename}"
    return os.path.join(user_dir, unique_name)


async def save_upload_file(file: UploadFile, user_id: int) -> tuple[str, str]:
    file_path = get_upload_path(user_id, file.filename)
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path, file.filename 


async def save_file_content(content: bytes, user_id: int, filename: str) -> tuple[str, str]:
    file_path = get_upload_path(user_id, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    return file_path, filename