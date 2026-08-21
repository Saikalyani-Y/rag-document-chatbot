from fastapi import APIRouter

from models.schemas import HealthOut
from services.llm_service import check_ollama_ready

router = APIRouter()


@router.get("/health", response_model=HealthOut)
def health() -> HealthOut:
    ok, detail = check_ollama_ready()
    return HealthOut(status="ok" if ok else "degraded", detail=detail)
