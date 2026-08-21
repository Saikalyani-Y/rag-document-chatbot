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
    document_id: str
    filename: str
    label: str
    chunk_id: int
    score: float


class MessageOut(BaseModel):
    id: str
    role: str
    content: str
    sources: Optional[list[SourceOut]] = None
    created_at: str


class SendMessageRequest(BaseModel):
    content: str


class SendMessageResponse(BaseModel):
    message_id: str
    answer: str
    sources: list[SourceOut]


class HealthOut(BaseModel):
    status: str
    detail: str
