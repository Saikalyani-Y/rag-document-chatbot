from typing import Optional

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    file_type: str
    status: str
    error_message: Optional[str] = None
    chunk_count: int
    uploaded_at: str


class ConversationOut(BaseModel):
    id: str
    title: str
    created_at: str
    updated_at: str


class SourceOut(BaseModel):
    kind: str = "document"  # "document" | "web"
    document_id: Optional[str] = None
    filename: str
    label: str
    chunk_id: int
    score: float
    url: Optional[str] = None


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[list[SourceOut]] = None
    grounded: bool = True
    created_at: str


class SendMessageRequest(BaseModel):
    content: str
    allow_general_knowledge: bool = False


class SendMessageResponse(BaseModel):
    message_id: str
    answer: str
    sources: list[SourceOut]
    grounded: bool


class HealthOut(BaseModel):
    status: str
    detail: str
