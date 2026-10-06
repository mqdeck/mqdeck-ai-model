from pathlib import Path

from pipeline.normalize import discover_custom


def test_custom_discovery_supports_structured_qna(tmp_path: Path) -> None:
    path = tmp_path / "qna" / "questions.yaml"
    path.parent.mkdir()
    path.write_text(
        "examples:\n  - question: How?\n    answer: Carefully.\n    language: en\n"
        "    license_class: public\n    license_id: MIT\n    copyright: Copyright Test\n"
        "    license_url: LICENSE\n",
        encoding="utf-8",
    )
    documents = discover_custom(tmp_path)
    assert len(documents) == 1
    assert documents[0].content == "Question: How?\n\nAnswer: Carefully."
    assert documents[0].source_path == "custom/qna/questions.yaml"
