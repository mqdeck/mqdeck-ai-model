from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    with path.open(encoding="utf-8") as handle:
        value = yaml.safe_load(handle) or {}
    return value


def hardware_summary() -> dict[str, Any]:
    import torch

    cuda = torch.cuda.is_available()
    if cuda:
        properties = torch.cuda.get_device_properties(0)
        return {
            "device": "cuda",
            "gpu": properties.name,
            "vram_gib": round(properties.total_memory / 1024**3, 2),
            "precision": "bf16" if torch.cuda.is_bf16_supported() else "fp16",
        }
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return {"device": "mps", "gpu": "Apple Metal", "vram_gib": None, "precision": "fp16"}
    return {"device": "cpu", "gpu": None, "vram_gib": None, "precision": "fp32"}


def count_jsonl(path: Path) -> int:
    with path.open(encoding="utf-8") as handle:
        return sum(1 for line in handle if line.strip())


def write_metadata(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
