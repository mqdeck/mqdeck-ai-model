from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

VALID_LICENSE_CLASSES = {"public", "restricted", "internal", "unknown"}


@dataclass(frozen=True)
class Document:
    id: str
    title: str
    product: str
    version: str
    category: str
    source_type: str
    source_url: str | None
    language: str
    license_class: str
    license_id: str
    retrieved_at: str | None
    content: str
    source_path: str | None = None
    copyright: str | None = None
    license_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Document:
        return cls(
            id=str(value["id"]),
            title=str(value["title"]),
            product=str(value["product"]),
            version=str(value["version"]),
            category=str(value["category"]),
            source_type=str(value["source_type"]),
            source_url=value.get("source_url"),
            language=str(value["language"]),
            license_class=str(value["license_class"]),
            license_id=str(value["license_id"]),
            retrieved_at=value.get("retrieved_at"),
            content=str(value["content"]),
            source_path=value.get("source_path"),
            copyright=value.get("copyright"),
            license_url=value.get("license_url"),
        )


@dataclass(frozen=True)
class SourceDecision:
    id: str
    url: str | None
    source: str
    source_path: str | None
    title: str
    version: str
    hash: str
    license_class: str
    license_id: str
    copyright: str | None
    license_url: str | None
    retrieval_timestamp: str | None
    included: bool
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
