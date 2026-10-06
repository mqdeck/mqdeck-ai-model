from __future__ import annotations

import argparse
import os
from pathlib import Path

from training.utils import load_yaml


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Merge a LoRA adapter into its configured base model."
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    config = load_yaml(root / "config" / "model.yaml")
    base_config = config["base_model"]
    model_id = str(base_config["model_id"])
    if base_config.get("license_id") not in {
        "Apache-2.0",
        "MIT",
        "BSD-2-Clause",
        "BSD-3-Clause",
    }:
        raise SystemExit("Base-model license is not on the commercial redistribution allowlist.")
    if not base_config.get("commercial_use_confirmed") or not base_config.get(
        "redistribution_confirmed"
    ):
        raise SystemExit("Base-model commercial and redistribution rights are not confirmed.")
    adapter_dir = root / "models" / "adapters" / args.version
    if not adapter_dir.exists():
        raise SystemExit(f"Adapter does not exist: {adapter_dir}")
    try:
        import torch
        from peft import PeftModel
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit(
            "Training dependencies are missing. Run: pip install -e '.[train]'"
        ) from exc
    token = os.environ.get("HF_TOKEN") or None
    base = AutoModelForCausalLM.from_pretrained(
        model_id,
        token=token,
        revision=str(base_config.get("revision", "main")),
        torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
        trust_remote_code=bool(config["base_model"].get("trust_remote_code", False)),
    )
    merged = PeftModel.from_pretrained(base, str(adapter_dir)).merge_and_unload()
    output = root / "models" / "merged" / args.version
    output.mkdir(parents=True, exist_ok=True)
    merged.save_pretrained(str(output), safe_serialization=True)
    AutoTokenizer.from_pretrained(adapter_dir).save_pretrained(str(output))
    print(f"Merged model written to {output}")


if __name__ == "__main__":
    main()
