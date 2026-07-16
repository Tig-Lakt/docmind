from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import func


class User(SQLModel, table=True):
    __tablename__ = "docmind_users"

    id:              int | None         = Field(default=None, primary_key=True)
    email:           str                = Field(unique=True, index=True)
    hashed_password: str
    is_active:       bool               = Field(default=True)
    is_superuser:    bool               = Field(default=False)
    created_at:      datetime = Field(
        default_factory=datetime.now,  # ← naive datetime
        sa_column_kwargs={"server_default": func.now()}
    )
    documents:       list["Document"]   = Relationship(back_populates="owner")