from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import String, func
from sqlalchemy.orm import mapped_column


class Document(SQLModel, table=True):
    __tablename__ = "docmind_documents"

    doc_id:             int       = Field(default=None, primary_key=True)
    user_id:            int       = Field(foreign_key="docmind_users.id", index=True)
    filename:           str       = Field(sa_column=mapped_column(String(255)))
    file_path:          str       = Field(sa_column=mapped_column(String(500)))
    file_type:          str       = Field(sa_column=mapped_column(String(10)))
    qdrant_collection:  str       = Field(sa_column=mapped_column(String(100)))
    created_at:      datetime = Field(
        default_factory=datetime.now,  # ← naive datetime
        sa_column_kwargs={"server_default": func.now()}
    )
    owner:              "User"    = Relationship(back_populates="documents")