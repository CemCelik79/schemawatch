# SchemaWatch

Detect breaking API changes automatically.

SchemaWatch compares two OpenAPI schemas and identifies breaking API changes before they reach production.

It is designed to be simple, fast, and CI/CD friendly.

---

## 🚀 Features

SchemaWatch detects:

- Removed endpoints
- Removed HTTP methods
- Removed schemas
- Removed response fields
- Field type changes
- Fields that became required

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/CemCelik79/schemawatch.git
cd schemawatch
## Install from PyPI

```bash
pip install schemawatch