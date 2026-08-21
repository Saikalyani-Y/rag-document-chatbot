"""Turns extracted document text into overlapping chunks with page/section tracking.

Documents are extracted as a list of "units" — pages for PDFs, paragraphs for
TXT/DOCX. Units are concatenated into one text with their offsets recorded, then
chunked as a whole (so chunks aren't awkwardly truncated at unit boundaries), and
each resulting chunk is tagged with the unit it started in for citations.
"""

import bisect
from dataclasses import dataclass


@dataclass
class Chunk:
    text: str
    chunk_index: int
    unit_number: int  # 1-indexed page (PDF) or section/paragraph (TXT/DOCX)


def _sliding_window(text: str, chunk_size: int, overlap: int) -> list[tuple[int, int, str]]:
    """Fixed-step sliding window over `text`, snapping chunk ends to whitespace when close."""
    step = max(chunk_size - overlap, 1)
    n = len(text)
    spans: list[tuple[int, int, str]] = []
    start = 0
    while start < n:
        end = min(start + chunk_size, n)
        if end < n:
            snap = text.rfind(" ", start, end)
            if snap > start + chunk_size // 2:
                end = snap
        piece = text[start:end].strip()
        if piece:
            spans.append((start, end, piece))
        start += step
    return spans


def chunk_units(units: list[str], chunk_size: int, overlap: int) -> list[Chunk]:
    """Concatenate units and chunk the combined text, tagging each chunk with its source unit."""
    offsets: list[int] = []
    full_text = ""
    for unit in units:
        offsets.append(len(full_text))
        full_text += unit.strip() + "\n\n"

    if not full_text.strip():
        return []

    spans = _sliding_window(full_text, chunk_size, overlap)
    chunks: list[Chunk] = []
    for i, (start, _end, text) in enumerate(spans):
        unit_idx = bisect.bisect_right(offsets, start) - 1
        unit_number = max(unit_idx, 0) + 1
        chunks.append(Chunk(text=text, chunk_index=i, unit_number=unit_number))
    return chunks
