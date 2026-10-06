# Adding custom knowledge

To teach MQDeck AI something new, place a Markdown, text, YAML, JSON, or JSONL file
under this directory and rebuild the dataset or model. No code change is required.

Choose the closest folder: `knowledge`, `runbooks`, `troubleshooting`, `commands`,
`qna`, or `examples`. Markdown files may start with YAML front matter. Always declare
the content's language and usage class when possible:

```yaml
---
title: My operational note
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

The default public build accepts only local content marked `public`, with an explicit
allowlisted `license_id`, copyright notice, and license reference. The initial allowlist
contains only `MIT`. Files with missing metadata, remote URLs, unknown licenses, or
third-party text are rejected. Do not paste vendor documentation or text from websites.
Add only original content owned by the contributor and released under the declared
license. Do not add secrets, credentials, customer data, access-controlled material, or
content you do not have authority to publish and commercialize.

Supported languages are English (`en`), Portuguese (`pt-BR`), and Spanish (`es`). The
model is instructed to answer in the question's language while leaving MQSC commands,
object names, and AMQ identifiers unchanged.
