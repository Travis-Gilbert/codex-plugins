---
description: "Bridge Django ORM with pandas/numpy/scipy: QuerySet-to-DataFrame, bulk ingest, computation pipelines"
allowed-tools: Read, Write, Edit, Bash, Grep, Glob, AskUserQuestion
argument-hint: "<data pipeline or conversion question>"
---

# Django Data Bridge

Load the data-bridge agent from `${CLAUDE_PLUGIN_ROOT}/agents/data-bridge.md` and follow its instructions.

Before bridging Django and scientific Python:

1. **Read** `${CLAUDE_PLUGIN_ROOT}/references/scientific-bridge.md` for the integration playbook
2. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/django-pandas/` for DataFrameManager and read_frame
3. **Grep** `${CLAUDE_PLUGIN_ROOT}/refs/dj-notebook/` for Jupyter integration

Apply memory rules based on data volume: <10K rows use values(), 10K-100K use values_list(named=True), >100K use iterator() or chunked SQL. Always specify exact fields and use batch_size for writes.
