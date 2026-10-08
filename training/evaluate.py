from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, cast

from training.utils import load_yaml, write_metadata


def concept_present(response: str, concept: str) -> bool:
    tokens = [token for token in re.findall(r"[A-Za-z0-9_*]+", concept.lower()) if len(token) > 2]
    normalized = response.lower()
    return bool(tokens) and sum(token in normalized for token in tokens) / len(tokens) >= 0.6


LANGUAGE_MARKERS = {
    "en": {"the", "use", "queue", "with", "current", "check"},
    "pt-BR": {"a", "de", "uma", "use", "fila", "com", "verifique", "substitua"},
    "es": {"la", "de", "una", "use", "cola", "con", "revise", "sustituya"},
}


def language_matches(response: str, expected: str) -> bool:
    words = set(re.findall(r"[A-Za-zÀ-ÿ]+", response.lower()))
    scores = {language: len(words & markers) for language, markers in LANGUAGE_MARKERS.items()}
    return scores.get(expected, 0) > 0 and scores.get(expected, 0) == max(scores.values())


def generate_responses(model_path: Path, cases: list[dict[str, Any]]) -> dict[str, str]:
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Evaluation dependencies are missing. Run: pip install -e '.[train]'"
        ) from exc
    tokenizer = AutoTokenizer.from_pretrained(str(model_path))
    model: Any = AutoModelForCausalLM.from_pretrained(
        str(model_path), device_map="auto" if torch.cuda.is_available() else None
    )
    responses: dict[str, str] = {}
    for case in cases:
        inputs: Any = cast(
            Any,
            tokenizer.apply_chat_template(
                [{"role": "user", "content": case["question"]}],
                add_generation_prompt=True,
                return_tensors="pt",
            ),
        )
        inputs = inputs.to(model.device)
        output = model.generate(inputs, max_new_tokens=384, do_sample=False)
        responses[case["id"]] = cast(
            str,
            tokenizer.decode(output[0][inputs.shape[-1] :], skip_special_tokens=True),
        )
    return responses


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate model responses by expected concepts.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--responses-json", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    cases = load_yaml(root / "evaluation" / "cases.yaml")["cases"]
    if args.responses_json:
        responses = json.loads(args.responses_json.read_text(encoding="utf-8"))
    else:
        responses = generate_responses(root / "models" / "merged" / args.version, cases)
    results = []
    for case in cases:
        response = responses.get(case["id"], "")
        checks = {
            concept: concept_present(response, concept) for concept in case["expected_concepts"]
        }
        expected_language = case.get("expected_language", "en")
        language_match = language_matches(response, expected_language)
        concept_score = sum(checks.values()) / len(checks)
        results.append(
            {
                "id": case["id"],
                "question": case["question"],
                "response": response,
                "concepts": checks,
                "expected_language": expected_language,
                "language_match": language_match,
                "score": (concept_score + float(language_match)) / 2,
            }
        )
    report = {
        "version": args.version,
        "mean_score": sum(item["score"] for item in results) / len(results),
        "results": results,
    }
    output = root / "models" / "adapters" / args.version / "evaluation.json"
    write_metadata(output, report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
