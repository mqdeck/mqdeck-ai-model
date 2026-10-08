from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import cast

from training.utils import count_jsonl, hardware_summary, load_yaml, write_metadata


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fine-tune the configured base model with LoRA or QLoRA."
    )
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--resume-from-checkpoint", default=None)
    args = parser.parse_args()
    root = args.root.resolve()
    config = load_yaml(root / "config" / "model.yaml")
    base_config = config["base_model"]
    model_id = str(base_config["model_id"])
    if base_config.get("license_id") not in {"Apache-2.0", "MIT", "BSD-2-Clause", "BSD-3-Clause"}:
        raise SystemExit("Base-model license is not on the commercial redistribution allowlist.")
    if not base_config.get("commercial_use_confirmed") or not base_config.get(
        "redistribution_confirmed"
    ):
        raise SystemExit("Confirm commercial use and redistribution rights in config/model.yaml.")

    try:
        import torch
        from datasets import load_dataset
        from peft import LoraConfig, prepare_model_for_kbit_training
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
        from trl import SFTConfig, SFTTrainer
    except ImportError as exc:
        raise SystemExit(
            "Training dependencies are missing. Run: pip install -e '.[train]'"
        ) from exc

    train_config = config["training"]
    hardware = hardware_summary()
    if train_config["method"] == "qlora" and hardware["device"] != "cuda":
        raise SystemExit(
            "QLoRA requires a compatible CUDA GPU and bitsandbytes. "
            f"Detected device: {hardware['device']}. Prepare the dataset on this host and train on a CUDA host."
        )

    output_dir = root / "models" / "adapters" / args.version
    output_dir.mkdir(parents=True, exist_ok=True)
    token = os.environ.get("HF_TOKEN") or None
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=token,
        revision=str(base_config.get("revision", "main")),
        trust_remote_code=bool(config["base_model"].get("trust_remote_code", False)),
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=bool(train_config["load_in_4bit"]),
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16,
        bnb_4bit_use_double_quant=True,
    )
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        token=token,
        revision=str(base_config.get("revision", "main")),
        quantization_config=quantization_config,
        device_map="auto",
        trust_remote_code=bool(config["base_model"].get("trust_remote_code", False)),
    )
    model = prepare_model_for_kbit_training(model)
    peft_config = LoraConfig(
        r=int(train_config["lora_r"]),
        lora_alpha=int(train_config["lora_alpha"]),
        lora_dropout=float(train_config["lora_dropout"]),
        target_modules=list(train_config["target_modules"]),
        bias="none",
        task_type="CAUSAL_LM",
    )
    data_files = {
        "train": str(root / "dataset" / "train" / "train.jsonl"),
        "validation": str(root / "dataset" / "validation" / "validation.jsonl"),
    }
    dataset = load_dataset("json", data_files=data_files)

    def format_row(row: dict[str, object]) -> dict[str, str]:
        messages = cast(list[dict[str, str]], row["messages"])
        return {
            "text": cast(
                str,
                tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=False
                ),
            )
        }

    dataset = dataset.map(format_row)
    sft_config = SFTConfig(
        output_dir=str(output_dir),
        num_train_epochs=float(train_config["epochs"]),
        learning_rate=float(train_config["learning_rate"]),
        per_device_train_batch_size=int(train_config["batch_size"]),
        per_device_eval_batch_size=1,
        gradient_accumulation_steps=int(train_config["gradient_accumulation_steps"]),
        max_length=int(train_config["max_seq_length"]),
        save_steps=int(train_config["save_steps"]),
        logging_steps=int(train_config["logging_steps"]),
        eval_strategy="steps",
        eval_steps=int(train_config["save_steps"]),
        bf16=torch.cuda.is_bf16_supported(),
        fp16=not torch.cuda.is_bf16_supported(),
        report_to="none",
        dataset_text_field="text",
    )
    trainer = SFTTrainer(
        model=model,
        args=sft_config,
        train_dataset=dataset["train"],
        eval_dataset=dataset["validation"],
        peft_config=peft_config,
        processing_class=tokenizer,
    )
    summary = {
        **hardware,
        "base_model": model_id,
        "base_model_revision": str(base_config.get("revision")),
        "base_model_license": str(base_config.get("license_id")),
        "method": train_config["method"],
        "train_samples": count_jsonl(Path(data_files["train"])),
        "validation_samples": count_jsonl(Path(data_files["validation"])),
        "version": args.version,
    }
    print(json.dumps(summary, indent=2))
    trainer.train(resume_from_checkpoint=args.resume_from_checkpoint)
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    write_metadata(output_dir / "training.json", summary)


if __name__ == "__main__":
    main()
