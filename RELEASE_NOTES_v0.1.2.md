## v0.1.2 — Operation-level diff

### New
- `compare_operations()`: requestBody ve response status code değişimlerini yakalar
- Request body field kaldırma / required olma tespiti
- Response status code kaldırma tespiti (critical)
- `$ref` ile tanımlı requestBody şemalarını resolve eder

### Fixed
- Roadmap: Request body change detection ✅
- Roadmap: Response status code comparison ✅
