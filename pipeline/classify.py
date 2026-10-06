from pipeline.models import Document, SourceDecision


def filter_by_license(
    documents: list[Document], allowed_classes: set[str], allowed_license_ids: set[str]
) -> tuple[list[Document], list[SourceDecision]]:
    included: list[Document] = []
    decisions: list[SourceDecision] = []
    for document in documents:
        accept = (
            document.license_class in allowed_classes
            and document.license_id in allowed_license_ids
            and bool(document.copyright)
            and bool(document.license_url)
            and document.source_url is None
        )
        if accept:
            included.append(document)
        decisions.append(
            SourceDecision(
                id=document.id,
                url=document.source_url,
                source=document.source_type,
                source_path=document.source_path,
                title=document.title,
                version=document.version,
                hash=document.id.removeprefix("sha256:"),
                license_class=document.license_class,
                license_id=document.license_id,
                copyright=document.copyright,
                license_url=document.license_url,
                retrieval_timestamp=document.retrieved_at,
                included=accept,
                reason=(
                    "explicit license and local-source policy accepted"
                    if accept
                    else "rejected: license, copyright, remote-source, or build-profile policy failed"
                ),
            )
        )
    return included, decisions
