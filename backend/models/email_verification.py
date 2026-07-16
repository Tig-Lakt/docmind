from datetime import datetime, timezone
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TIMESTAMP


class EmailVerification(SQLModel, table=True):
    __tablename__ = "docmind_email_verifications"

    id:         int      = Field(default=None, primary_key=True)
    email:      str      = Field(index=True)
    code:       str      = Field(max_length=6)
    expires_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )
    is_used:    bool     = Field(default=False)
    created_at: datetime = Field(
        sa_column=Column(TIMESTAMP(timezone=True), nullable=False)
    )