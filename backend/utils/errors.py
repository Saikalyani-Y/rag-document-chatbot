import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger("rag_chatbot")


class AppError(Exception):
    """Base class for errors that should be shown to the user as a clean message."""

    status_code = 500

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class UnsupportedFormatError(AppError):
    status_code = 415


class FileTooLargeError(AppError):
    status_code = 413


class EmptyFileError(AppError):
    status_code = 422


class DuplicateDocumentError(AppError):
    status_code = 409


class DocumentProcessingError(AppError):
    status_code = 422


class NotFoundError(AppError):
    status_code = 404


class LLMServiceError(AppError):
    status_code = 503


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError):
        return JSONResponse(status_code=exc.status_code, content={"error": exc.message})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        logger.exception("Unhandled error on %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "Something went wrong on our end. Please try again."},
        )
