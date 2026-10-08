# Contributing

Thank you for helping improve MQDeck AI Model. Repository documentation, code, commit
messages, and pull-request descriptions must be written in English. Training examples may
also be written in Portuguese or Spanish when they are original and properly licensed.

## Development setup

```bash
./scripts/setup.sh
make lint
make test
```

Use `./scripts/run.sh --dry-run` to inspect the Ubuntu GPU workflow without changing the
machine. Do not commit generated datasets, model weights, caches, credentials, or logs.

## Training-source requirements

Every contributed training source must be original content that the contributor is
authorized to publish under the MIT license for commercial model training, modification,
and redistribution. It must contain the metadata required by `custom/README.md`.

Do not contribute vendor documentation, website text, support content, books, forum posts,
customer data, logs, credentials, access-controlled material, or close paraphrases of
third-party content. Read `SOURCE_POLICY.md` before changing anything under `custom/`.

## Pull requests

- Keep each pull request focused and explain its user-visible effect.
- Add or update tests for behavior changes.
- Run `make lint` and `make test` before submission.
- Update the README, changelog, model card, notices, or source policy when applicable.
- Never weaken provenance, license, safety, or destructive-action checks merely to pass a
  build.

By contributing repository code or original examples, you agree that your contribution is
provided under the applicable MIT license in this repository.
