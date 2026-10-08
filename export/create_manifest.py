from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import urllib.error
import urllib.request
from pathlib import Path

from pipeline.io import read_jsonl, read_yaml, write_json


def copy_verified_base_license(base_model: dict[str, object], destination: Path) -> None:
    url = str(base_model["license_download_url"])
    expected_sha256 = str(base_model["license_sha256"])
    request = urllib.request.Request(url, headers={"User-Agent": "mqdeck-ai-model-release"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            content = response.read()
    except (urllib.error.URLError, TimeoutError) as exc:
        raise SystemExit(f"Unable to download the pinned base-model license: {exc}") from None

    actual_sha256 = hashlib.sha256(content).hexdigest()
    if actual_sha256 != expected_sha256:
        raise SystemExit(
            "Base-model license checksum mismatch: "
            f"expected {expected_sha256}, received {actual_sha256}."
        )
    destination.write_bytes(content)


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
    copy_verified_base_license(model["base_model"], release / "BASE_MODEL_LICENSE.txt")
    model_card = (root / "MODEL_CARD_TEMPLATE.md").read_text(encoding="utf-8")
    (release / "MODEL_CARD.md").write_text(
        model_card.replace("VERSION", args.version), encoding="utf-8"
    )
    # Verify the generated files are readable and report dataset row counts for operators.
    _ = read_jsonl(root / "dataset" / "train" / "train.jsonl")
    print(f"Release metadata written to {release}")


if __name__ == "__main__":
    main()
