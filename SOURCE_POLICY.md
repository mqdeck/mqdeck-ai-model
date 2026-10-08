# Public and commercial source policy

This policy is an engineering safeguard, not a guarantee against legal claims or a
substitute for qualified legal review.

## Default policy

The public build uses only local, original content placed under `custom/` by contributors
who own the content and intentionally license it for commercial use, modification, model
training, and redistribution. Remote collection and website crawling are not implemented.

Every source must declare:

- `license_class: public`;
- an allowlisted SPDX `license_id`;
- a copyright notice;
- a local or authoritative license reference;
- no remote `source_url`.

The initial public allowlist contains only `MIT`, matching `DATASET_LICENSE`. Unknown,
restricted, copied, scraped, or incompletely documented sources fail closed.

## Prohibited training content

Do not add:

- IBM product documentation, IBM website text, IBM software, or IBM support content;
- text copied or paraphrased from a vendor publication without an applicable license;
- Stack Overflow, forum, issue, blog, book, course, video, or social-media content;
- customer data, support tickets, logs, queue contents, credentials, endpoints, or secrets;
- third-party generated datasets without a completed license and provenance review;
- content subject to non-commercial, research-only, no-derivatives, confidential, or
  redistribution-restricted terms.

Links may be retained as factual citations in a human review record, but linked content is
not ingested. Public accessibility does not establish training or redistribution rights.

## Original technical knowledge

Contributors may write original explanations of facts, workflows, commands, observations,
and operational experience they are authorized to publish. Avoid reproducing expressive
vendor wording, diagrams, tables, examples, or documentation structure. Validate technical
claims independently and preserve contributor identity and license records.

## Base model

The exact base-model revision must have an allowlisted permissive license and explicit
commercial-use and redistribution confirmations. The default is Qwen/Qwen3-0.6B under
Apache-2.0, pinned to revision `c1899de289a04d12100db370d81485cdf75e47ca`.
Training and merge scripts refuse to continue when those confirmations are not present.
Re-verify the exact remote model card and license immediately before a public release
because upstream metadata can change.

## Release review

Before distributing a dataset, adapter, merged model, or GGUF:

1. Review `sources.json` and confirm every entry is included under the public policy.
2. Confirm the exact base-model revision and retain its license and notices.
3. Include `LICENSE`, `DATASET_LICENSE`, `THIRD_PARTY_NOTICES.md`, and a completed model card.
4. Run provenance, secret, personal-data, memorization, safety, and output-regression checks.
5. Confirm that the release name and presentation do not imply vendor affiliation.
6. Obtain counsel review for the intended jurisdictions and commercial distribution plan.
