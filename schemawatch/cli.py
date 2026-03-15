import sys
import sys
import json
import yaml


from schemawatch.parser import load_openapi_file
from schemawatch.diff_engine import detect_breaking_changes



def load_schema(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def check(old_schema_path, new_schema_path):

    old_schema = load_schema(old_schema_path)
    new_schema = load_schema(new_schema_path)

    changes = detect_breaking_changes(old_schema, new_schema)

    if changes:
        print("⚠ Breaking API changes detected:\n")

        for change in changes:
            print("-", change["message"])

        sys.exit(1)

    print("✅ No breaking changes detected")
    sys.exit(0)


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage:")
        print("schemawatch old_schema.yaml new_schema.yaml")
        sys.exit(1)

    check(sys.argv[1], sys.argv[2])


def main():
    if len(sys.argv) != 4:
        print("Kullanım:")
        print("python -m schemawatch.cli diff old.yaml new.yaml")
        return

    command = sys.argv[1]
    old_file = sys.argv[2]
    new_file = sys.argv[3]

    if command != "diff":
        print("Sadece diff komutu destekleniyor")
        return

    old_schema = load_openapi_file(old_file)
    new_schema = load_openapi_file(new_file)

    changes = detect_breaking_changes(old_schema, new_schema)

    if changes:
        print("BREAKING CHANGES:")
        for change in changes:
            print("-", change["message"])
    else:
        print("Breaking change yok")


if __name__ == "__main__":
    main()
