import json
import sys
from pathlib import Path

from schemawatch.diff_engine import detect_breaking_changes
from schemawatch.parser import load_openapi_file


def format_text_output(changes):
    lines = ["⚠ Breaking API changes detected:\n"]
    for change in changes:
        lines.append(f"- {change['message']}")
    return "\n".join(lines)


def build_result(old_schema_path, new_schema_path, changes):
    return {
        "breaking_changes_detected": bool(changes),
        "summary": {
            "total_changes": len(changes),
            "breaking_changes": len(changes),
        },
        "files": {
            "old_schema": str(old_schema_path),
            "new_schema": str(new_schema_path),
        },
        "changes": changes,
    }


def write_output_file(output_path, content):
    path = Path(output_path)
    path.write_text(content, encoding="utf-8")


def check(old_schema_path: str, new_schema_path: str):
    old_schema = load_openapi_file(old_schema_path)
    new_schema = load_openapi_file(new_schema_path)

    changes = detect_breaking_changes(old_schema, new_schema)
    return changes


def print_usage():
    print("Usage:")
    print(
        "python -m schemawatch.cli <old_schema.yaml> <new_schema.yaml> "
        "[--format text|json] [--output result.json] [--quiet]"
    )


def main():
    args = sys.argv[1:]

    if len(args) < 2:
        print_usage()
        sys.exit(1)

    old_schema_path = args[0]
    new_schema_path = args[1]

    output_format = "text"
    output_file = None
    quiet = False

    i = 2
    while i < len(args):
        arg = args[i]

        if arg == "--format":
            if i + 1 >= len(args):
                print("Error: --format requires a value (text or json)")
                sys.exit(1)
            output_format = args[i + 1].lower()
            if output_format not in {"text", "json"}:
                print("Error: --format must be 'text' or 'json'")
                sys.exit(1)
            i += 2
            continue

        if arg == "--output":
            if i + 1 >= len(args):
                print("Error: --output requires a file path")
                sys.exit(1)
            output_file = args[i + 1]
            i += 2
            continue

        if arg == "--quiet":
            quiet = True
            i += 1
            continue

        print(f"Error: Unknown argument: {arg}")
        print_usage()
        sys.exit(1)

    changes = check(old_schema_path, new_schema_path)
    result = build_result(old_schema_path, new_schema_path, changes)

    if output_format == "json":
        content = json.dumps(result, indent=2, ensure_ascii=False)
    else:
        content = (
            format_text_output(changes)
            if changes
            else "✅ No breaking changes detected"
        )

    if output_file:
        write_output_file(output_file, content)

    if not quiet:
        print(content)

    sys.exit(1 if changes else 0)


if __name__ == "__main__":
    main()