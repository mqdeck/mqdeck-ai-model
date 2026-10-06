from pathlib import Path

from pipeline.dataset_builder import build_examples
from pipeline.io import read_yaml
from pipeline.normalize import discover_custom

ROOT = Path(__file__).resolve().parents[1]


def test_target_languages_have_grounded_examples() -> None:
    documents = discover_custom(ROOT / "custom")
    examples = build_examples(documents, "System")
    languages = {example["source_language"] for example in examples}
    assert {"en", "pt-BR", "es"} <= languages
    for example in examples:
        if example["source_language"] in {"pt-BR", "es"}:
            question = example["messages"][1]["content"]
            answer = example["messages"][2]["content"]
            assert question and answer


def test_system_prompt_requires_question_language() -> None:
    prompt = read_yaml(ROOT / "config" / "training.yaml")["dataset"]["system_prompt_en"]
    assert "Always answer in the language used by the user's question" in prompt
    assert "English, Portuguese, or Spanish" in prompt
