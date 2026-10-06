from pipeline.models import Document


def deduplicate(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    unique: list[Document] = []
    duplicates: list[Document] = []
    seen: set[str] = set()
    for document in documents:
        if document.id in seen:
            duplicates.append(document)
        else:
            seen.add(document.id)
            unique.append(document)
    return unique, duplicates
