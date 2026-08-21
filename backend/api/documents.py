from fastapi import APIRouter, UploadFile

import db
from models.schemas import DocumentOut
from services import document_service

router = APIRouter()


@router.post("/documents", response_model=DocumentOut, status_code=201)
async def upload_document(file: UploadFile) -> DocumentOut:
    content = await file.read()
    document = document_service.process_upload(file.filename, content)
    return DocumentOut(**document)


@router.get("/documents", response_model=list[DocumentOut])
def list_documents() -> list[DocumentOut]:
    return [DocumentOut(**dict(row)) for row in db.list_documents()]


@router.delete("/documents/{document_id}", status_code=204)
def delete_document(document_id: str) -> None:
    document_service.delete_document(document_id)
