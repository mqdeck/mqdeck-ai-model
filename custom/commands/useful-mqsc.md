---
title: Useful MQSC Observation Commands
product: MQ-compatible messaging
category: commands
version: generic
language: en
license_class: public
license_id: MIT
copyright: Copyright (c) 2026 MQDeck contributors
license_url: LICENSE
---

# Useful MQSC observation commands

```text
DISPLAY QLOCAL(MY.QUEUE) CURDEPTH
DISPLAY QSTATUS(MY.QUEUE) ALL
DISPLAY CHSTATUS(*)
DISPLAY LSSTATUS(*)
DISPLAY QMGR ALL
```

Confirm the target queue manager and object name before issuing commands. These commands
observe state; they do not by themselves establish the root cause of a problem.
