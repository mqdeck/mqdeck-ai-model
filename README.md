# MQDeck AI Model

MQDeck AI Model is a reproducible pipeline that prepares licensed training data, fine-tunes
`Qwen/Qwen3-0.6B` with QLoRA, evaluates the result, and exports a ready-to-use GGUF model.
The model answers in English, Portuguese, or Spanish, matching the language of the question.

> **Independent project:** MQDeck AI is not affiliated with, endorsed by, sponsored by,
> supported by, or certified by IBM. IBM and IBM MQ are trademarks of International
> Business Machines Corporation in the United States and/or other countries. References are
> descriptive only.

No IBM documentation, website content, software, support material, customer data, or other
remotely collected content is included in the training data. The repository has no crawler.

## One-command build

Use an Ubuntu machine with:

- Ubuntu 24.04 LTS x86-64 (recommended; Ubuntu 22.04 is also accepted);
- an NVIDIA GPU with compute capability 7.0 or newer;
- 6 GiB GPU VRAM minimum, 8 GiB or more recommended;
- 16 GiB system RAM and 30 GiB free storage recommended;
- internet access for Ubuntu, PyTorch, Hugging Face, and `llama.cpp` downloads.

Compatibility sources:

- [Ubuntu NVIDIA driver guide](https://ubuntu.com/server/docs/how-to/graphics/install-nvidia-drivers/)
- [PyTorch installation guidance](https://pytorch.org/get-started/locally/)
- [bitsandbytes hardware requirements](https://huggingface.co/docs/bitsandbytes/main/en/installation)
- [llama.cpp build guide](https://github.com/ggml-org/llama.cpp/blob/master/docs/build.md)

From the repository root, run:

```bash
./scripts/ubuntu.sh
```

That command installs the required Ubuntu packages, creates `.venv`, installs the pinned
CUDA training stack, validates the GPU, prepares `llama.cpp`, builds the dataset, trains and
evaluates the model, and exports the release.

If no working NVIDIA driver is present, the script installs the driver recommended by
Ubuntu and stops. Reboot once, return to the repository, and run the same command again.
The script is idempotent and continues from the prepared environment.
For an uninterrupted first run, start from an Ubuntu GPU image where `nvidia-smi` already
works with a current driver.

The default output is:

```text
models/releases/0.1.0/mqdeck-ai-0.1.0-Q4_K_M.gguf
```

To choose a release version:

```bash
./scripts/ubuntu.sh --version 1.0.0
```

Use `./scripts/ubuntu.sh --help` to see the small set of supported options. A safe preview
is available with `./scripts/ubuntu.sh --dry-run`.

## Add your own training knowledge

Place original files owned by you or your organization under `custom/`. Supported formats
are Markdown, text, YAML, JSON, and JSONL. A Markdown source starts with metadata like this:

```yaml
---
title: Queue backlog triage
product: MQ-compatible messaging
category: troubleshooting
version: generic
language: en
license_class: public
license_id: MIT
copyright: Copyright (c) 2026 Your organization
license_url: LICENSE
---
```

Then run the same one-command build again:

```bash
./scripts/ubuntu.sh --version 1.0.0
```

The public build fails closed when source ownership, license, provenance, or required
metadata is missing. Do not add vendor documentation, website text, forum content, books,
customer data, logs, credentials, or any material you are not authorized to use for model
training and commercial redistribution. See [SOURCE_POLICY.md](SOURCE_POLICY.md).

## Useful commands

```bash
# Prepare and validate only the dataset; no GPU is required
./scripts/ubuntu.sh --prepare-only

# Build on a machine that was already prepared
./scripts/build-model.sh --version 1.0.0

# Create a local development environment and run checks
./scripts/setup.sh
make lint
make test
```

Generated datasets, source decisions, training metadata, evaluation results, checksums, and
GGUF files are stored under `dataset/`, `sources/manifests/`, and
`models/releases/<version>/`.

## Language and safety behavior

Training examples and evaluation cases cover English, Brazilian Portuguese, and Spanish.
The system policy requires answers in the language used by the question while preserving
commands, object names, and message identifiers. It also requires observation before
changes, clear separation of facts from hypotheses, and explicit warnings and confirmation
before destructive actions.

## Licensing and distribution

- Repository code: MIT, in [LICENSE](LICENSE).
- Original bundled training data: MIT, in [DATASET_LICENSE](DATASET_LICENSE).
- Pinned base model: `Qwen/Qwen3-0.6B`, Apache-2.0, at revision
  `c1899de289a04d12100db370d81485cdf75e47ca`.
- Base-model source and license: [Qwen/Qwen3-0.6B on Hugging Face](https://huggingface.co/Qwen/Qwen3-0.6B/tree/c1899de289a04d12100db370d81485cdf75e47ca).

The pipeline uses only local sources explicitly marked for public MIT-licensed use. These
controls reduce licensing risk but do not guarantee freedom from claims or replace legal
review. Before public or commercial distribution, review every source record, recheck the
exact base-model license, scan for secrets and personal data, complete the model card,
retain all required notices, and obtain qualified legal review for the intended use.

Read [NOTICE.md](NOTICE.md), [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md), and
[MODEL_CARD_TEMPLATE.md](MODEL_CARD_TEMPLATE.md) before publishing a release.

## Limitations

The bundled corpus is intentionally small and is not sufficient for an authoritative
production assistant. Model output can be incomplete, inaccurate, or unsafe. Human review
is mandatory before operational changes. This project is not vendor documentation or a
source of vendor support.
