import re
from pydantic import BaseModel
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[a-zA-Zа-яА-Я]", v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DocumentResponse(BaseModel):
    doc_id: int
    filename: str
    file_type: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    doc_id: int
    question: str

    @field_validator("question")
    @classmethod
    def question_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Вопрос не может быть пустым")
        return v.strip()


class ChatResponse(BaseModel):
    answer: str
    chunks_found: int


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не менее 8 символов")
        if not re.search(r"\d", v):
            raise ValueError("Пароль должен содержать хотя бы одну цифру")
        if not re.search(r"[a-zA-Zа-яА-Я]", v):
            raise ValueError("Пароль должен содержать хотя бы одну букву")
        return v
    

class PasswordResetRequest(BaseModel):
    email: EmailStr


class RegisterInitResponse(BaseModel):
    message: str

class ConfirmRegistration(BaseModel):
    email: EmailStr
    code: str

class ResendCode(BaseModel):
    email: EmailStr