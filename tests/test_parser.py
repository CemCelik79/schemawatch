import pytest

from schemawatch.parser import load_openapi_file


def test_load_openapi_file_success(tmp_path):
    file_path = tmp_path / "openapi.yaml"
    file_path.write_text(
        """
openapi: 3.0.0
info:
  title: Test API
  version: 1.0.0
paths: {}
""".strip(),
        encoding="utf-8",
    )

    data = load_openapi_file(str(file_path))
    assert data["openapi"] == "3.0.0"


def test_load_openapi_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_openapi_file("does-not-exist.yaml")


def test_load_openapi_file_empty_file(tmp_path):
    file_path = tmp_path / "empty.yaml"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="Dosya boş veya geçerli YAML değil"):
        load_openapi_file(str(file_path))


def test_load_openapi_file_not_openapi(tmp_path):
    file_path = tmp_path / "not_openapi.yaml"
    file_path.write_text(
        """
info:
  title: Invalid
paths: {}
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Bu dosya OpenAPI formatında değil"):
        load_openapi_file(str(file_path))