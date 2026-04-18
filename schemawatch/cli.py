import sys
from schemawatch.parser import load_openapi_file
from schemawatch.diff_engine import detect_breaking_changes


def check(old_schema_path: str, new_schema_path: str) -> int:
    old_schema = load_openapi_file(old_schema_path)
    new_schema = load_openapi_file(new_schema_path)

    changes = detect_breaking_changes(old_schema, new_schema)

    if changes:
        print("⚠ Breaking API changes detected:\n")
        for change in changes:
            print("-", change["message"])
        return 1

    print("✅ No breaking changes detected")
    return 0


def main():
    # Kullanım:
    # python -m schemawatch.cli old.yaml new.yaml
    if len(sys.argv) != 3:
        print("Usage:")
        print("python -m schemawatch.cli old_schema.yaml new_schema.yaml")
        sys.exit(1)

    exit_code = check(sys.argv[1], sys.argv[2])
    sys.exit(exit_code)


if __name__ == "__main__":
    main()