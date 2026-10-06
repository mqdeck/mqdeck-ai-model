from pipeline.dataset_builder import build_examples
from pipeline.models import Document
from pipeline.split_dataset import split_examples
from pipeline.validate_dataset import validate_examples


def document(identifier: str, content: str = "Question: How?\n\nAnswer: Safely.") -> Document:
    return Document(
        id=identifier,
        title=f"Title {identifier}",
        product="MQ-compatible messaging",
        version="generic",
        category="qna",
        source_type="custom",
        source_url=None,
        language="en",
        license_class="public",
        license_id="MIT",
        retrieved_at=None,
        content=content,
    )


def test_dataset_generation_preserves_provenance() -> None:
    examples = build_examples([document("sha256:1")], "System")
    assert examples[0]["source_ids"] == ["sha256:1"]
    assert examples[0]["messages"][1]["content"] == "How?"
    assert validate_examples(examples) == []


def test_dataset_split_is_deterministic_and_complete() -> None:
    examples = [
        build_examples([document(f"sha256:{i}", f"Text {i}")], "System")[0] for i in range(20)
    ]
    first = split_examples(examples, 0.9, 0.05, 0.05, 42)
    second = split_examples(examples, 0.9, 0.05, 0.05, 42)
    assert first == second
    assert {key: len(value) for key, value in first.items()} == {
        "train": 18,
        "validation": 1,
        "test": 1,
    }


def test_dataset_rejects_unsafe_destructive_command() -> None:
    examples = build_examples(
        [document("sha256:1", "Question: Fix it?\n\nAnswer: CLEAR QLOCAL(A)")], "System"
    )
    assert "destructive command" in validate_examples(examples)[0]
