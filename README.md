# SchemaWatch

![PyPI](https://img.shields.io/pypi/v/schemawatch)
![CI](https://github.com/CemCelik79/schemawatch/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/pypi/pyversions/schemawatch)
![License](https://img.shields.io/github/license/CemCelik79/schemawatch)

Detect breaking API changes automatically.

SchemaWatch compares two OpenAPI schemas and identifies breaking API changes before they reach production.

It is designed to be simple, fast, and CI/CD friendly.

---

## 🚀 Features

SchemaWatch detects:

* Removed endpoints
* Removed HTTP methods
* Removed schemas
* Removed response fields
* Field type changes
* Fields that became required

---

## 📦 Installation

```bash
pip install schemawatch
```

---

## ⚙️ Usage

### Basic usage

```bash
schemawatch examples/old.yaml examples/new.yaml
```

---

### JSON output

```bash
schemawatch examples/old.yaml examples/new.yaml --format json
```

---

### Save output to file

```bash
schemawatch examples/old.yaml examples/new.yaml --format json --output result.json
```

---

## 🧪 Example Output

```text
⚠ Breaking API changes detected:

- Method removed: GET /users
- Endpoint removed: /orders
- Response field removed: User.email
- Field type changed: User.id integer -> string
- Field became required: User.id
```

---

## 🔁 CI/CD Integration

SchemaWatch is designed to run in CI pipelines.

```bash
schemawatch openapi_old.yaml openapi.yaml
```

* Exit code `1` → breaking changes detected ❌
* Exit code `0` → no breaking changes ✅

---

## 💬 PR Comment Integration

SchemaWatch can automatically comment on pull requests:

```
⚠ Breaking API changes detected:

- Method removed: GET /users
- Field type changed: User.id integer -> string
```

---

## 📂 Project Structure

```
schemawatch/
├─ schemawatch/
├─ tests/
├─ examples/
├─ README.md
├─ requirements.txt
└─ pyproject.toml
```

---

## 🛠 Roadmap

* Request body change detection
* Response status code comparison
* Enum change detection
* Nested object comparison improvements
* Markdown / HTML output

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 📄 License

MIT License

---

## ⭐ Why SchemaWatch?

Most OpenAPI diff tools are heavy or complex.

SchemaWatch focuses on:

* ⚡ Simplicity
* ⚡ Speed
* ⚡ CI/CD integration

> "Know when your API breaks — before it reaches production."
