from pathlib import Path
import yaml


def load_openapi_file(file_path: str):

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Dosya bulunamadı: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if "openapi" not in data:
        raise ValueError("Bu dosya OpenAPI formatında değil")

    return data