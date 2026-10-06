from __future__ import annotations

from pipeline.models import Document


def chunk_document(document: Document, max_chars: int = 6000) -> list[Document]:
    """Split on paragraph boundaries while retaining source identity and metadata."""
    if len(document.content) <= max_chars:
        return [document]
    chunks: list[str] = []
    current: list[str] = []
    size = 0
    for paragraph in document.content.split("\n\n"):
        if current and size + len(paragraph) + 2 > max_chars:
            chunks.append("\n\n".join(current))
            current, size = [], 0
        current.append(paragraph)
        size += len(paragraph) + 2
    if current:
        chunks.append("\n\n".join(current))
    return [
        Document(
            **{
                **document.to_dict(),
                "id": f"{document.id}:chunk:{index + 1}",
                "title": f"{document.title} (part {index + 1})",
                "content": content,
            }
        )
        for index, content in enumerate(chunks)
    ]
