---
title: Consumer Stopped
product: MQ-compatible messaging
category: troubleshooting
version: generic
language: en
license_class: public
license_id: MIT
copyright: Copyright (c) 2026 MQDeck contributors
license_url: LICENSE
---

# Consumer stopped

Observed values:

```text
CURDEPTH: 85000
MAXDEPTH: 100000
IPPROCS: 0
OPPROCS: 12
```

The confirmed facts are that messages are present, no input handles are currently open,
and output handles are open. A plausible hypothesis is that the expected consumer is not
connected, but these values alone do not prove why. Check the consumer application,
queue status, connections, related channels, and logs before changing the queue.
