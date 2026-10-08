# MQDeck AI Model

MQDeck AI Model is an independent pipeline for building a public, commercially usable
messaging-operations language model from explicitly licensed, project-owned training data.
It prepares source-grounded instruction datasets, fine-tunes with LoRA/QLoRA, evaluates the
result, and exports GGUF files for `llama.cpp` and `llama-server`.

> **Independent project:** MQDeck AI is not affiliated with, endorsed by, sponsored by,
> supported by, or certified by IBM. IBM and IBM MQ are trademarks of International
> Business Machines Corporation in the United States and/or other countries. References are
> descriptive only. The model and artifacts are branded `MQDeck AI`, not IBM or IBM MQ.

No IBM documentation, website corpus, software, support content, customer material, or
remotely collected content is included. The project has no crawler and does not follow
links in source files. See [NOTICE.md](NOTICE.md) and [SOURCE_POLICY.md](SOURCE_POLICY.md).

## License design

- Pipeline source code: MIT, in `LICENSE`.
- Bundled original training data: MIT, in `DATASET_LICENSE`.
- Default base model: `Qwen/Qwen3-4B`, Apache-2.0.
- Generated model: subject to the base-model license, dataset license, included notices,
  and the completed model card.

The default build accepts only original local documents marked `public`, licensed `MIT`,
with copyright and license metadata. Unknown, remote, copied, or incompletely documented
sources are rejected. This is a conservative engineering control, not a guarantee against
legal claims; obtain qualified review before a material public or commercial release.

## Architecture

```text
original licensed files under custom/
        |
        v
normalize -> SHA-256 deduplicate -> commercial-license policy
        |
        v
source-grounded multilingual chat examples with source_ids
        |
        v
validate -> deterministic train/validation/test split
        |
        v
QLoRA adapter -> concept/language evaluation -> merged model
        |
        v
official llama.cpp converter -> F16 -> quantized GGUF -> public release
```

There is no database, vector store, RAG service, crawler, API, frontend, or dependency on
the main MQDeck application.

## Requirements

- Python 3.10 or newer.
- CPU for preparation, tests, and validation.
- A compatible NVIDIA CUDA GPU and `bitsandbytes` for default QLoRA training.
- Storage for the base model, adapter, merged model, F16 GGUF, and quantized GGUF.
- `cmake`, a C/C++ toolchain, and an official `llama.cpp` checkout for conversion.
- Re-verification of the exact base-model revision and license before release.

## Quick start

On Ubuntu with an NVIDIA GPU, from a fresh checkout:

```bash
./scripts/ubuntu.sh
```

The script installs build tools, a CUDA PyTorch environment, and `llama-quantize`, then trains and writes the final GGUF. If the NVIDIA driver is missing, it installs `nvidia-driver-570` and stops so you can reboot and run the same command again.

The finished file is `models/releases/0.1.0/mqdeck-ai-0.1.0-Q4_K_M.gguf`. The configured base model is `Qwen/Qwen3-0.6B`, which fits a 6 GB card such as a GTX 1660.

Inspect:

```text
dataset/generated/all.jsonl
dataset/generated/statistics.json
dataset/train/train.jsonl
dataset/validation/validation.jsonl
dataset/test/test.jsonl
sources/manifests/sources.json
```

For training on a compatible CUDA host:

```bash
pip install -e '.[train]'
./scripts/build-model.sh --version 0.1.0
```

The base model defaults to [Qwen/Qwen3-4B](https://huggingface.co/Qwen/Qwen3-4B), whose
model card identifies it as Apache-2.0 and compatible with `llama.cpp`. The exact revision
and license must still be rechecked before every public release.

## Adding original knowledge

Add original material owned by you or your organization under `custom/`. No code change is
required. Supported extensions are `.md`, `.txt`, `.yaml`, `.yml`, `.json`, and `.jsonl`.

```yaml
---
title: Queue Backlog Triage
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

Then prepare and review:

```bash
cp queue-backlog.md custom/troubleshooting/
./scripts/prepare.sh
```

Do not paste or paraphrase vendor documentation, books, websites, support cases, forum
answers, customer logs, or other third-party text. Write original explanations based on
authorized experience and independently verified facts. The public build fails closed if
license, copyright, or provenance metadata is absent.

## Languages

The initial dataset supports English (`en`), Portuguese (`pt-BR`), and Spanish (`es`). The
system prompt requires the model to answer in the language of the user's question while
preserving commands, object names, and message identifiers. Include high-quality original
examples in each target language rather than relying on unreviewed automatic translation.

## Source and license validation

`config/source_policy.yaml` controls eligible sources. The initial public allowlist contains
only `MIT`. A source is accepted only when it:

- is local and has no remote `source_url`;
- is explicitly marked `public`;
- uses an allowlisted SPDX license identifier;
- has a copyright notice and license reference;
- passes dataset quality and operational-safety validation.

`sources.json` records the source path, hash, copyright, license, inclusion decision, and
reason without embedding full document content.

The optional `private` profile exists for authorized internal experiments, but artifacts
from it must not be published or commercialized unless every source is separately cleared.
Public release automation should always use the default `public` profile.

## Dataset generation and safety

Preparation normalizes documents, hashes and deduplicates content, enforces the source
policy, produces source-grounded chat examples, validates them, and creates deterministic
90/5/5 splits. Small datasets keep at least one validation and one test example.

Every example contains `source_ids`. Validation rejects empty records, duplicate questions,
oversized examples, placeholders, missing provenance, and destructive commands without a
safety warning.

The system policy instructs the model to:

- observe and diagnose before changing state;
- distinguish confirmed facts from hypotheses;
- request missing evidence;
- avoid invented commands, attributes, message identifiers, or behavior;
- never recommend destructive actions without impact explanation and confirmation;
- avoid using capacity increases to conceal an unresolved backlog.

## Training and checkpoints

The default model configuration is in `config/model.yaml`. It records the model ID,
revision, license identifier, license URL, and explicit commercial-use and redistribution
confirmations. Training and merge refuse to proceed if these checks are absent or if the
license is outside the permissive allowlist.

```bash
./scripts/train.sh --version 1.0.0

./scripts/train.sh \
  --version 1.0.0 \
  --resume-from-checkpoint models/adapters/1.0.0/checkpoint-100
```

QLoRA is the default; full fine-tuning is not. Checkpoints and training metadata are stored
under `models/adapters/<version>/`.

## Evaluation

```bash
./scripts/evaluate.sh --version 1.0.0
```

Evaluation checks expected concepts and whether responses follow the language of the
question. Extend `evaluation/cases.yaml` with original regression, safety, multilingual,
and adversarial cases before release.

## GGUF export

Use an existing official `llama.cpp` checkout:

```bash
export LLAMA_CPP_PATH=/opt/llama.cpp
./scripts/export.sh --version 1.0.0
```

Or explicitly allow a clone under `work/llama.cpp`:

```bash
export ALLOW_LLAMA_CPP_CLONE=1
./scripts/export.sh --version 1.0.0
```

The release contains:

```text
models/releases/1.0.0/
├── mqdeck-ai-1.0.0-F16.gguf
├── mqdeck-ai-1.0.0-Q4_K_M.gguf
├── manifest.json
├── sources.json
├── evaluation.json
├── training.json
└── checksums.json
```

Copy `MODEL_CARD_TEMPLATE.md`, `LICENSE`, `DATASET_LICENSE`, and
`THIRD_PARTY_NOTICES.md` into the public release package after completing release-specific
details.

## Running locally

```bash
llama-server \
  -m models/releases/1.0.0/mqdeck-ai-1.0.0-Q4_K_M.gguf \
  --ctx-size 8192 \
  --port 8080
```

## Commands

```bash
make setup
make prepare
make train VERSION=1.0.0
make evaluate VERSION=1.0.0
make export VERSION=1.0.0
make build VERSION=1.0.0
make lint
make test
make clean

./scripts/build-model.sh --version 1.0.0 --prepare-only
./scripts/build-model.sh --version 1.0.0 --dry-run
./scripts/build-model.sh --version 1.0.0
```

`--custom-only` remains accepted for compatibility but is now redundant: every build uses
only local `custom/` content. Remote collection is not implemented.

## Release checklist

Before publishing or commercial use:

1. Run `make lint` and `make test`.
2. Run a clean public-profile dataset build.
3. Review every `sources.json` entry.
4. Scan source and generated data for secrets and personal or customer information.
5. Recheck the exact base-model revision and retain its Apache-2.0 license.
6. Run safety, memorization, multilingual, and operational regression evaluation.
7. Complete the model card and include all licenses and notices.
8. Confirm product naming does not imply vendor affiliation.
9. Obtain qualified legal review for intended markets and distribution channels.

## Limitations

- The bundled corpus is intentionally small and must be expanded with original licensed
  material before it can produce a reliable specialist model.
- PDF and remote-source ingestion are deliberately unsupported.
- Technical references to IBM MQ remain necessary to describe interoperability and domain
  behavior, but the project does not include IBM-authored training content.
- A model can hallucinate unsafe guidance despite training controls. Human review remains
  mandatory for operational changes.
- No technical design can guarantee freedom from legal claims; the project provides
  conservative controls and evidence for professional review.
