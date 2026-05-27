# SchemaWatch

> Detect breaking API changes before they reach production.
> Works with any OpenAPI file — just run one command.

![PyPI](https://img.shields.io/pypi/v/schemawatch)
![CI](https://github.com/CemCelik79/schemawatch/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/pypi/pyversions/schemawatch)
![License](https://img.shields.io/github/license/CemCelik79/schemawatch)
![Stars](https://img.shields.io/github/stars/CemCelik79/schemawatch?style=social)

---

## 🎬 Demo

![SchemaWatch Demo](docs/demo.gif)

```bash
python -m schemawatch.cli examples/old.yaml examples/new.yaml
```

---

## 🚀 What is SchemaWatch?

SchemaWatch compares two OpenAPI schemas and detects breaking API changes automatically.

It is designed to be:

- ⚡ Simple
- ⚡ Fast
- ⚡ CI/CD friendly

---

## 🚀 Features

SchemaWatch detects:

- Removed endpoints
- Removed HTTP methods
- Removed schemas
- Removed response fields
- Field type changes
- Fields that became required
- Enum value changes
- Array item type changes
- `$ref` resolution for `components.schemas` and request/response bodies

### How reporting works

SchemaWatch checks breaking changes at two levels:

1. **Component schemas** (`components.schemas`) — e.g. `Response field removed: User.email`
2. **Operations** (per path/method) — e.g. request body removed, response status removed

When a request or response body is **only** a `$ref` to a component schema (e.g. `#/components/schemas/User`), field-level changes are reported **once** at the schema level, not again as `Response body field removed: GET /users 200.email`. Inline body schemas (no `$ref`) are still reported at the operation level.

---

## 📦 Installation

```bash
pip install schemawatch
```

---

## ⚙️ Usage

```bash
# Basic usage
python -m schemawatch.cli examples/old.yaml examples/new.yaml

# JSON output
python -m schemawatch.cli examples/old.yaml examples/new.yaml --format json

# Markdown output
python -m schemawatch.cli examples/old.yaml examples/new.yaml --format markdown

# Save to file
python -m schemawatch.cli examples/old.yaml examples/new.yaml --format json --output result.json

# Quiet mode (CI use)
python -m schemawatch.cli examples/old.yaml examples/new.yaml --quiet
```

---

## 🧑‍💻 Real-world usage

```bash
python -m schemawatch.cli openapi_old.yaml openapi.yaml
python -m schemawatch.cli api/v1/openapi.yaml api/v2/openapi.yaml
```

---

## 🧪 Example Output

```
====================================
🚨 SchemaWatch Report
====================================

Breaking changes detected: 5

── CRITICAL (2)
🔴 Endpoint removed: /orders
🔴 Method removed: GET /users

── WARNING (3)
🟡 Response field removed: User.email
🟡 Field type changed: User.id integer -> string
🟡 Field became required: User.id

------------------------------------
Summary:
- Total changes: 5
- Critical: 2
- Warning:  3
- Info:     0
------------------------------------
```

---

## 🔁 CI/CD Integration

SchemaWatch is designed to run in CI pipelines.

```bash
python -m schemawatch.cli openapi_old.yaml openapi.yaml
```

- Exit code `1` → breaking changes detected ❌
- Exit code `0` → no breaking changes ✅

---

## ⚙️ GitHub Actions Example

```yaml
- name: Check API breaking changes
  run: python -m schemawatch.cli openapi_old.yaml openapi.yaml
```

---

## 💬 PR Comment Integration

Automatically comments on pull requests:

```
⚠ Breaking API changes detected:

🔴 Endpoint removed: /orders
🟡 Field type changed: User.id integer -> string
```

---

## 🤔 Why not oasdiff / openapi-diff?

| Feature        | SchemaWatch         | oasdiff / openapi-diff |
| -------------- | ------------------- | ---------------------- |
| Easy CLI       | ✅ Very simple       | ⚠️ More complex        |
| CI/CD friendly | ✅ Built-in mindset  | ⚠️ Needs config        |
| PR comments    | ✅ Yes               | ❌ Not built-in         |
| Severity levels| ✅ Critical/Warning/Info | ❌ Not built-in    |
| Output         | ✅ Clean & readable  | ⚠️ Verbose             |
| Setup time     | ⚡ 10 seconds        | ⏱️ Longer              |

> SchemaWatch = quick setup + practical usage

---

## 🛠 Roadmap

- [x] Request body change detection
- [x] Response status code comparison
- [x] `$ref` resolution (`#/components/...` internal pointers)
- [ ] Nested object comparison improvements (`allOf` / `oneOf`, external file refs)
- [x] Markdown output (`--format markdown`)
- [ ] HTML output
- [ ] Web dashboard

---
## 🤖 AI-Powered Explanations (Experimental)

SchemaWatch can use Gemma 4 to explain breaking changes in plain English.

```bash
python gemma_explainer.py
```

Requires a Google AI Studio API key:

1. Get your free API key from [Google AI Studio](https://aistudio.google.com)
2. Create a `.env` file: `GEMINI_API_KEY=your_key_here`
3. Run: `python gemma_explainer.py`

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a pull request

---

## 💬 Feedback

Found a bug or want a feature?
[Open an issue](https://github.com/CemCelik79/schemawatch/issues/new) —
even a one-liner helps.

---

## 📄 License

This project is licensed under the MIT License.