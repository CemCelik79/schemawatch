# SchemaWatch

Detect breaking API changes automatically.

SchemaWatch compares two OpenAPI schemas and detects breaking API changes before they reach production.

It can run locally, in CI/CD pipelines, or inside GitHub Actions.

---

# Features

SchemaWatch detects:

- Removed endpoints
- Removed response fields
- Field type changes
- Fields that became required

This helps teams prevent breaking API changes from being merged.

---

# Example

Run schema comparison:

bash

python -m schemawatch.cli openapi_old.yaml openapi.yaml
Output:

⚠ Breaking API changes detected:

- Method removed: GET /users
- Response field removed: User.email
- Field type changed: User.id integer -> string
- Field became required: User.id