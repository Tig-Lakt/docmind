#document_service.py
ALLOWED_TYPES = {"pdf", "docx", "xlsx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 МБ

#file_storage.py
UPLOAD_DIR = "uploads"

#qdrant_service.py
VECTOR_SIZE = 1536  # text-embedding-3-small

#email_recovery_service.py
TOKEN_EXPIRE_HOURS = 1