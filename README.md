# SchemaWatch

SchemaWatch is a developer tool that detects breaking API schema changes before they reach production.

## Current MVP Scope

This first version can detect:

- removed endpoints
- removed HTTP methods
- removed response fields
- changed field types
- fields that became required

## Tech Stack

- Python
- PyYAML
- pytest

## Project Structure

```text
schemawatch/
├─ schemawatch/
│  ├─ __init__.py
│  ├─ cli.py
│  ├─ parser.py
│  ├─ diff_engine.py
│  └─ rules.py
├─ examples/
│  ├─ old.yaml
│  └─ new.yaml
├─ tests/
│  └─ test_diff_engine.py
└─ requirements.txt