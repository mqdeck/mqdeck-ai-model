from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml

from pipeline.models import VALID_LICENSE_CLASSES, Document

SUPPORTED_SUFFIXES = {".md", ".txt", ".yaml", ".yml", ".json", ".jsonl"}
FRONTMATTER = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONTMATTER.match(text)
    if not match:
        return {}, text
    metadata = yaml.safe_load(match.group(1)) or {}
    if not isinstance(metadata, dict):
        raise TypeError("Markdown front matter must be a mapping")
    return metadata, match.group(2)


def content_hash(content: str) -> str:
    return hashlib.sha256(normalize_text(content).encode("utf-8")).hexdigest()


def _structured_records(path: Path) -> Iterator[tuple[dict[str, Any], str]]:
    if path.suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    elif path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
    else:
        with path.open(encoding="utf-8") as handle:
            data = [json.loads(line) for line in handle if line.strip()]
    records = data.get("examples", data) if isinstance(data, dict) else data
    if isinstance(records, dict):
        records = [records]
    if not isinstance(records, list):
        raise TypeError(f"Structured content must contain a list or object: {path}")
    for record in records:
        if not isinstance(record, dict):
            continue
        if "question" in record and "answer" in record:
            content = f"Question: {record['question']}\n\nAnswer: {record['answer']}"
        else:
            content = json.dumps(record, ensure_ascii=False, sort_keys=True)
        yield record, content


def load_custom_file(path: Path, custom_root: Path) -> list[Document]:
    if path.suffix.lower() not in SUPPORTED_SUFFIXES:
        return []
    category = path.relative_to(custom_root).parts[0] if path != custom_root else "knowledge"
    rows: list[tuple[dict[str, Any], str]]
    if path.suffix.lower() in {".md", ".txt"}:
        metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))
        rows = [(metadata, body)]
    else:
        rows = list(_structured_records(path))
    documents: list[Document] = []
    for index, (metadata, raw_content) in enumerate(rows):
        content = normalize_text(raw_content)
        if not content:
            continue
        license_class = str(metadata.get("license_class", "unknown"))
        if license_class not in VALID_LICENSE_CLASSES:
            raise ValueError(f"Invalid license_class '{license_class}' in {path}")
        license_id = str(metadata.get("license_id", "unknown"))
        digest = content_hash(content)
        suffix = f" #{index + 1}" if len(rows) > 1 else ""
        documents.append(
            Document(
                id=f"sha256:{digest}",
                title=str(metadata.get("title", path.stem.replace("-", " ").title())) + suffix,
                product=str(metadata.get("product", "MQ-compatible messaging")),
                version=str(metadata.get("version", "generic")),
                category=str(metadata.get("category", category)),
                source_type="custom",
                source_url=None,
                language=str(metadata.get("language", "en")),
                license_class=license_class,
                license_id=license_id,
                retrieved_at=None,
                content=content,
                source_path=str(Path("custom") / path.relative_to(custom_root)),
                copyright=metadata.get("copyright"),
                license_url=metadata.get("license_url"),
            )
        )
    return documents


def discover_custom(custom_root: Path) -> list[Document]:
    documents: list[Document] = []
    for path in sorted(custom_root.rglob("*")):
        if path.is_file() and path.name != "README.md":
            documents.extend(load_custom_file(path, custom_root))
    return documents
