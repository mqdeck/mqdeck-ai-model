from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

from pipeline.classify import filter_by_license
from pipeline.dataset_builder import build_examples
from pipeline.deduplicate import deduplicate
from pipeline.io import read_yaml, write_json, write_jsonl
from pipeline.normalize import discover_custom
from pipeline.split_dataset import split_examples
from pipeline.validate_dataset import validate_examples

LOGGER = logging.getLogger("mqdeck.prepare")


def prepare(root: Path, profile: str, custom_only: bool = False) -> dict[str, int]:
    sources_config = read_yaml(root / "config" / "source_policy.yaml")
    training_config = read_yaml(root / "config" / "training.yaml")["dataset"]
    class_profiles = sources_config["build"]["allowed_license_classes"]
    license_profiles = sources_config["build"]["allowed_license_ids"]
    if profile not in class_profiles or profile not in license_profiles:
        raise ValueError(f"Unknown build profile: {profile}")

    documents = discover_custom(root / "custom")
    unique, duplicates = deduplicate(documents)
    included, decisions = filter_by_license(
        unique, set(class_profiles[profile]), set(license_profiles[profile])
    )

    if not included:
        raise ValueError(
            f"No documents are eligible for the '{profile}' build profile. "
            "Review source rights and classifications; do not weaken the filter merely to pass a build."
        )

    normalized_path = root / "sources" / "normalized" / "documents.jsonl"
    write_jsonl(normalized_path, (document.to_dict() for document in included))
    write_json(root / "sources" / "manifests" / "sources.json", [d.to_dict() for d in decisions])

    examples = build_examples(included, str(training_config["system_prompt_en"]))
    errors = validate_examples(examples, int(training_config["max_example_chars"]))
    if errors:
        raise ValueError("Dataset validation failed:\n- " + "\n- ".join(errors))
    write_jsonl(root / "dataset" / "generated" / "all.jsonl", examples)

    split = split_examples(
        examples,
        float(training_config["train"]),
        float(training_config["validation"]),
        float(training_config["test"]),
        int(training_config["seed"]),
    )
    for name, rows in split.items():
        write_jsonl(root / "dataset" / name / f"{name}.jsonl", rows)

    stats = {
        "discovered_documents": len(documents),
        "documents": len(included),
        "duplicates": len(duplicates),
        "excluded": len(unique) - len(included),
        "examples": len(examples),
        **{name: len(rows) for name, rows in split.items()},
    }
    write_json(root / "dataset" / "generated" / "statistics.json", stats)
    LOGGER.info("Preparation statistics: %s", stats)
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a traceable instruction dataset.")
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--profile", choices=["public", "private"], default="public")
    parser.add_argument("--custom-only", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        stats = prepare(args.root.resolve(), args.profile, args.custom_only)
    except (TypeError, ValueError) as exc:
        raise SystemExit(f"Preparation failed: {exc}") from None
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
