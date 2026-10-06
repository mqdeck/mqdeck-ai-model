from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify and checksum a GGUF release directory.")
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    release = args.root.resolve() / "models" / "releases" / args.version
    required = [
        "manifest.json",
        "sources.json",
        "evaluation.json",
        "training.json",
        "LICENSE",
        "DATASET_LICENSE",
        "THIRD_PARTY_NOTICES.md",
        "MODEL_CARD.md",
    ]
    missing = [name for name in required if not (release / name).exists()]
    if missing:
        raise SystemExit(f"Incomplete release metadata: {', '.join(missing)}")
    files = sorted(release.glob("*.gguf"))
    if not files:
        raise SystemExit(f"No GGUF artifacts found in {release}")
    checksums = {path.name: sha256(path) for path in files}
    (release / "checksums.json").write_text(
        json.dumps(checksums, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Release verified: {release}")


if __name__ == "__main__":
    main()
