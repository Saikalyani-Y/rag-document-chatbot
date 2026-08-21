import json
import uuid

from fastapi import APIRouter

import db
from models.schemas import ConversationOut, MessageOut, SendMessageRequest, SendMessageResponse
from services import rag_service
from utils.errors import DocumentProcessingError, NotFoundError

router = APIRouter()


@router.post("/conversations", response_model=ConversationOut, status_code=201)
def create_conversation() -> ConversationOut:
    conversation_id = str(uuid.uuid4())
    db.create_conversation(conversation_id)
    return ConversationOut(**dict(db.get_conversation(conversation_id)))


@router.get("/conversations", response_model=list[ConversationOut])
def list_conversations() -> list[ConversationOut]:
    return [ConversationOut(**dict(row)) for row in db.list_conversations()]


@router.delete("/conversations/{conversation_id}", status_code=204)
def delete_conversation(conversation_id: str) -> None:
    if db.get_conversation(conversation_id) is None:
        raise NotFoundError("Conversation not found.")
    db.delete_conversation(conversation_id)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def list_messages(conversation_id: str) -> list[MessageOut]:
    if db.get_conversation(conversation_id) is None:
        raise NotFoundError("Conversation not found.")
    rows = db.list_messages(conversation_id)
    return [
        MessageOut(
            id=row["id"],
            role=row["role"],
            content=row["content"],
            sources=json.loads(row["sources"]) if row["sources"] else None,
            grounded=bool(row["grounded"]),
            created_at=row["created_at"],
        )
        for row in rows
    ]


@router.post("/conversations/{conversation_id}/messages", response_model=SendMessageResponse)
def send_message(conversation_id: str, body: SendMessageRequest) -> SendMessageResponse:
    if db.get_conversation(conversation_id) is None:
        raise NotFoundError("Conversation not found.")

    question = body.content.strip()
    if not question:
        raise DocumentProcessingError("Message cannot be empty.")

    # Build history from prior turns before this question is persisted, so it isn't
    # duplicated (once via history, once as the explicit current turn) in the LLM prompt.
    result = rag_service.answer_question(conversation_id, question, allow_general=body.allow_general_knowledge)

    db.insert_message(str(uuid.uuid4()), conversation_id, "user", question)
    db.maybe_set_conversation_title(conversation_id, question)

    message_id = str(uuid.uuid4())
    db.insert_message(
        message_id, conversation_id, "assistant", result["answer"], result["sources"], result["grounded"]
    )
    db.touch_conversation(conversation_id)

    return SendMessageResponse(
        message_id=message_id, answer=result["answer"], sources=result["sources"], grounded=result["grounded"]
    )
