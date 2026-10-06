from __future__ import annotations

from typing import Any

from pipeline.models import Document
from pipeline.qa_generator import grounded_pair


def build_examples(documents: list[Document], system_prompt: str) -> list[dict[str, Any]]:
    examples: list[dict[str, Any]] = []
    for document in documents:
        question, answer = grounded_pair(document)
        examples.append(
            {
                "source_ids": [document.id],
                "source_language": document.language,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": answer},
                ],
            }
        )
    return examples
