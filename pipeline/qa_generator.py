from __future__ import annotations

import re

from pipeline.models import Document

QUESTION_ANSWER = re.compile(r"\AQuestion:\s*(.*?)\n\nAnswer:\s*(.*)\Z", re.DOTALL)

QUESTION_TEMPLATES = {
    "en": "What should an engineer know about {title}?",
    "pt-BR": "O que um engenheiro deve saber sobre {title}?",
    "pt": "O que um engenheiro deve saber sobre {title}?",
    "es": "¿Qué debe saber un ingeniero sobre {title}?",
}


def grounded_pair(document: Document) -> tuple[str, str]:
    """Build an extractive example; it never adds facts outside the source."""
    match = QUESTION_ANSWER.match(document.content)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    language = document.language if document.language in QUESTION_TEMPLATES else "en"
    question = QUESTION_TEMPLATES[language].format(title=document.title)
    return question, document.content
