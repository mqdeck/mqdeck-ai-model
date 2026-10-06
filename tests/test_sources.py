from pipeline.classify import filter_by_license
from pipeline.deduplicate import deduplicate
from pipeline.models import Document


def make_document(identifier: str, license_class: str, remote: bool = False) -> Document:
    return Document(
        id=identifier,
        title="Source",
        product="MQ-compatible messaging",
        version="generic",
        category="documentation",
        source_type="custom",
        source_url="https://example.com/source" if remote else None,
        language="en",
        license_class=license_class,
        license_id="MIT",
        retrieved_at=None,
        content="Content",
        copyright="Copyright Test",
        license_url="LICENSE",
    )


def test_license_filter_and_source_manifest_decision() -> None:
    included, decisions = filter_by_license(
        [make_document("sha256:public", "public"), make_document("sha256:unknown", "unknown")],
        {"public"},
        {"MIT"},
    )
    assert [item.id for item in included] == ["sha256:public"]
    assert decisions[1].included is False
    assert decisions[1].hash == "unknown"
    assert "content" not in decisions[1].to_dict()


def test_deduplication_uses_document_hash_id() -> None:
    unique, duplicate = deduplicate(
        [make_document("sha256:same", "public"), make_document("sha256:same", "public")]
    )
    assert len(unique) == 1
    assert len(duplicate) == 1


def test_remote_source_is_rejected_even_with_allowed_license() -> None:
    included, decisions = filter_by_license(
        [make_document("sha256:remote", "public", remote=True)], {"public"}, {"MIT"}
    )
    assert included == []
    assert decisions[0].included is False


def test_missing_copyright_is_rejected() -> None:
    document = make_document("sha256:no-copyright", "public")
    object.__setattr__(document, "copyright", None)
    included, _ = filter_by_license([document], {"public"}, {"MIT"})
    assert included == []
