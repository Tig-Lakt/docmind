from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP


class PasswordResetToken(SQLModel, table=True):
    __tablename__ = "docmind_password_reset_tokens"
    id:         int      = Field(default=None, primary_key=True)
    user_id:    int      = Field(foreign_key="docmind_users.id", index=True)
    token:      str      = Field(unique=True, index=True)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    is_used:    bool     = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    owner: "User" = Relationship()