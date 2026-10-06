from pathlib import Path

from pipeline.normalize import content_hash, load_custom_file, normalize_text, split_frontmatter


def test_markdown_normalization_and_frontmatter(tmp_path: Path) -> None:
    path = tmp_path / "knowledge" / "note.md"
    path.parent.mkdir()
    path.write_text(
        "---\ntitle: Test Note\nlanguage: en\nlicense_class: public\nlicense_id: MIT\n"
        "copyright: Copyright Test\nlicense_url: LICENSE\n---\n\nLine one.  \r\n\r\n\r\nLine two.\n",
        encoding="utf-8",
    )
    document = load_custom_file(path, tmp_path)[0]
    assert document.title == "Test Note"
    assert document.content == "Line one.\n\nLine two."


def test_frontmatter_and_hash_are_stable() -> None:
    metadata, body = split_frontmatter("---\ntitle: A\n---\nBody\n")
    assert metadata["title"] == "A"
    assert body == "Body\n"
    assert content_hash("Body\r\n") == content_hash(normalize_text("Body\n"))
