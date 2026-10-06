---
title: Queue Manager
product: MQ-compatible messaging
category: knowledge
version: generic
language: en
license_class: public
license_id: MIT
copyright: Copyright (c) 2026 MQDeck contributors
license_url: LICENSE
---

# Queue Manager

A queue manager is the central component that manages messaging objects and messages in
the environment described by these original project notes.
Common objects include local queues, remote queues, alias queues, channels, listeners,
topics, and subscriptions.

Useful observation commands include:

```text
DISPLAY QMGR
DISPLAY QLOCAL(*)
DISPLAY CHANNEL(*)
```
