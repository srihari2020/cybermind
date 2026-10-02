from datetime import datetime, timezone
from pydantic import BaseModel, Field, HttpUrl


class DocumentMetadata(BaseModel):
    source_id: str
    title: str
    publisher: str
    source_url: HttpUrl | None = None
    source_type: str = "document"
    version: str | None = None
    published_date: str | None = None
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    license: str | None = None
    sha256: str


class DocumentChunk(BaseModel):
    chunk_id: str
    source_id: str
    chunk_index: int
    text: str
    metadata: DocumentMetadata