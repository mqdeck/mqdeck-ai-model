from __future__ import annotations

import re
from typing import Any

PLACEHOLDER = re.compile(r"\b(TODO|TBD|FIXME|LOREM IPSUM)\b", re.IGNORECASE)
DESTRUCTIVE = re.compile(r"\b(CLEAR\s+QLOCAL|DELETE\s+Q\w*)\b", re.IGNORECASE)
SAFETY_TERMS = re.compile(
    r"\b(impact|confirm|backup|destructive|loss|warning|caution)\b", re.IGNORECASE
)


def validate_examples(examples: list[dict[str, Any]], max_chars: int = 16000) -> list[str]:
    errors: list[str] = []
    seen_questions: set[str] = set()
    for index, example in enumerate(examples, start=1):
        messages = example.get("messages", [])
        question = next((m.get("content", "") for m in messages if m.get("role") == "user"), "")
        answer = next((m.get("content", "") for m in messages if m.get("role") == "assistant"), "")
        label = f"example {index}"
        if not question.strip() or not answer.strip():
            errors.append(f"{label}: empty question or answer")
        normalized_question = " ".join(question.lower().split())
        if normalized_question in seen_questions:
            errors.append(f"{label}: duplicate question")
        seen_questions.add(normalized_question)
        if len(question) + len(answer) > max_chars:
            errors.append(f"{label}: exceeds maximum character count")
        if not example.get("source_ids"):
            errors.append(f"{label}: missing source_ids")
        if PLACEHOLDER.search(question) or PLACEHOLDER.search(answer):
            errors.append(f"{label}: contains a placeholder")
        if DESTRUCTIVE.search(answer) and not SAFETY_TERMS.search(answer):
            errors.append(f"{label}: destructive command lacks a safety warning")
    return errors
