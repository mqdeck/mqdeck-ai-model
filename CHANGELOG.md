# Changelog

All notable changes to MQDeck AI Model are documented in this file.

The project follows [Semantic Versioning](https://semver.org/).

## [0.1.0] - 2026-10-08

### Added

- One-command Ubuntu NVIDIA setup and model build through `scripts/run.sh`.
- Reproducible QLoRA training stack for the pinned `Qwen/Qwen3-0.6B` revision.
- English, Portuguese, and Spanish response-language policy and evaluation cases.
- GGUF conversion, quantization, release metadata, and checksum generation.
- GitHub Actions checks for tests, formatting, typing, and shell syntax.

### Security and licensing

- Public builds accept only original, local, MIT-licensed training sources with explicit
  provenance and copyright metadata.
- Remote collection, website crawling, and private or proprietary source profiles are
  disabled.
- The exact Apache-2.0 base-model license is downloaded, checksum-verified, and included in
  generated model releases.
- Independent-project, trademark, operational-safety, and legal-review notices are included.

[0.1.0]: https://github.com/mqdeck/mqdeck-ai-model/releases/tag/v0.1.0
