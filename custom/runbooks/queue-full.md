---
title: Queue Full Runbook
product: MQ-compatible messaging
category: runbook
version: generic
language: en
license_class: public
license_id: MIT
copyright: Copyright (c) 2026 MQDeck contributors
license_url: LICENSE
---

# Queue full

Symptom: an application reports that a queue reached its maximum depth.

Begin with observation: inspect `CURDEPTH`, `MAXDEPTH`, `IPPROCS`, `OPPROCS`, the
consumer application, the backlog pattern, and relevant application and queue-manager
logs.

```text
DISPLAY QLOCAL(MY.QUEUE) CURDEPTH MAXDEPTH IPPROCS OPPROCS
```

Do not increase `MAXDEPTH` merely to hide a backlog. Establish why messages are
accumulating and assess storage and operational impact before changing configuration.
