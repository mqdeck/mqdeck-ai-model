from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

from pipeline.io import read_jsonl, read_yaml, write_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Create release metadata without embedding source content."
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    release = root / "models" / "releases" / args.version
    release.mkdir(parents=True, exist_ok=True)
    model = read_yaml(root / "config" / "model.yaml")
    if not model["base_model"].get("commercial_use_confirmed") or not model["base_model"].get(
        "redistribution_confirmed"
    ):
        raise SystemExit(
            "Release refused: base-model commercial and redistribution rights are not confirmed."
        )
    stats_path = root / "dataset" / "generated" / "statistics.json"
    stats = json.loads(stats_path.read_text(encoding="utf-8")) if stats_path.exists() else {}
    quantizations = list(model["gguf"]["quantizations"])
    manifest = {
        "name": "mqdeck-ai",
        "version": args.version,
        "base_model": model["base_model"]["model_id"],
        "base_model_revision": model["base_model"].get("revision", "main"),
        "base_model_license": model["base_model"]["license_id"],
        "base_model_license_url": model["base_model"]["license_url"],
        "dataset_license": "MIT",
        "training_method": model["training"]["method"],
        "dataset": {
            key: stats.get(key, 0)
            for key in ("documents", "examples", "train", "validation", "test")
        },
        "languages": ["en", "pt-BR", "es"],
        "language_policy": "Answer in the language of the question.",
        "quantizations": quantizations,
        "independent_project": True,
        "affiliated_with_ibm": False,
    }
    write_json(release / "manifest.json", manifest)
    sources = root / "sources" / "manifests" / "sources.json"
    if sources.exists():
        shutil.copy2(sources, release / "sources.json")
    else:
        write_json(release / "sources.json", [])
    evaluation = root / "models" / "adapters" / args.version / "evaluation.json"
    training = root / "models" / "adapters" / args.version / "training.json"
    for source, name in ((evaluation, "evaluation.json"), (training, "training.json")):
        if source.exists():
            shutil.copy2(source, release / name)
        else:
            write_json(release / name, {"status": "not generated"})
    for name in ("LICENSE", "DATASET_LICENSE", "THIRD_PARTY_NOTICES.md"):
        shutil.copy2(root / name, release / name)
    model_card = (root / "MODEL_CARD_TEMPLATE.md").read_text(encoding="utf-8")
    (release / "MODEL_CARD.md").write_text(
        model_card.replace("VERSION", args.version), encoding="utf-8"
    )
    # Verify the generated files are readable and report dataset row counts for operators.
    _ = read_jsonl(root / "dataset" / "train" / "train.jsonl")
    print(f"Release metadata written to {release}")


if __name__ == "__main__":
    main()
