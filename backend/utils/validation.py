from pathlib import Path

from utils.errors import EmptyFileError, FileTooLargeError, UnsupportedFormatError

ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx"}


def validate_upload(filename: str, size_bytes: int, max_size_mb: int) -> str:
    """Validate an uploaded file and return its normalized extension (without the dot)."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise UnsupportedFormatError(f"Unsupported file type '{ext or 'unknown'}'. Allowed types: {allowed}")

    if size_bytes == 0:
        raise EmptyFileError("The uploaded file is empty.")

    max_bytes = max_size_mb * 1024 * 1024
    if size_bytes > max_bytes:
        raise FileTooLargeError(f"File exceeds the {max_size_mb}MB size limit.")

    return ext.lstrip(".")
