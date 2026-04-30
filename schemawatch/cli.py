import json
import sys
from pathlib import Path

from schemawatch.diff_engine import detect_breaking_changes
from schemawatch.parser import load_openapi_file
from colorama import Fore, Style, init

init(autoreset=True)

SEVERITY_ICON = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
}

SEVERITY_COLOR = {
    "critical": Fore.RED,
    "warning": Fore.YELLOW,
    "info": Fore.CYAN,
}


def format_text_output(changes):
    if not changes:
        return (
            f"\n{Fore.CYAN}===================================={Style.RESET_ALL}\n"
            f"{Fore.CYAN}🚨 SchemaWatch Report{Style.RESET_ALL}\n"
            f"{Fore.CYAN}===================================={Style.RESET_ALL}\n\n"
            f"{Fore.GREEN}✅ No breaking changes detected{Style.RESET_ALL}\n\n"
            f"{Fore.YELLOW}------------------------------------{Style.RESET_ALL}\n"
            f"{Fore.YELLOW}Summary:{Style.RESET_ALL}\n"
            f"- Total changes: 0\n"
            f"- Breaking changes: 0\n"
            f"{Fore.YELLOW}------------------------------------{Style.RESET_ALL}\n"
        )

    critical = [c for c in changes if c.get("severity") == "critical"]
    warnings = [c for c in changes if c.get("severity") == "warning"]
    infos = [c for c in changes if c.get("severity") == "info"]

    lines = [
        f"{Fore.CYAN}===================================={Style.RESET_ALL}",
        f"{Fore.CYAN}🚨 SchemaWatch Report{Style.RESET_ALL}",
        f"{Fore.CYAN}===================================={Style.RESET_ALL}",
        "",
        f"{Fore.RED}Breaking changes detected: {len(changes)}{Style.RESET_ALL}",
        "",
    ]

    for group, label in [(critical, "CRITICAL"), (warnings, "WARNING"), (infos, "INFO")]:
        if group:
            color = SEVERITY_COLOR.get(label.lower(), Fore.WHITE)
            icon = SEVERITY_ICON.get(label.lower(), "•")
            lines.append(f"{color}── {label} ({len(group)}){Style.RESET_ALL}")
            for c in group:
                lines.append(f"{color}  {icon} {c['message']}{Style.RESET_ALL}")
            lines.append("")

    lines.extend([
        f"{Fore.YELLOW}------------------------------------{Style.RESET_ALL}",
        f"{Fore.YELLOW}Summary:{Style.RESET_ALL}",
        f"- Total changes: {len(changes)}",
        f"- Critical: {len(critical)}",
        f"- Warning:  {len(warnings)}",
        f"- Info:     {len(infos)}",
        f"{Fore.YELLOW}------------------------------------{Style.RESET_ALL}",
    ])

    return "\n".join(lines)


def format_markdown_output(changes):
    if not changes:
        return (
            "# 🚨 SchemaWatch Report\n\n"
            "## ✅ No breaking changes detected\n\n"
            "## Summary\n\n"
            "- Total changes: 0\n"
        )

    critical = [c for c in changes if c.get("severity") == "critical"]
    warnings = [c for c in changes if c.get("severity") == "warning"]
    infos = [c for c in changes if c.get("severity") == "info"]

    lines = [
        "# 🚨 SchemaWatch Report",
        "",
        f"## Breaking changes detected: {len(changes)}",
        "",
    ]

    for group, label, icon in [
        (critical, "Critical", "🔴"),
        (warnings, "Warning", "🟡"),
        (infos, "Info", "🔵"),
    ]:
        if group:
            lines.append(f"### {icon} {label} ({len(group)})")
            lines.append("")
            for c in group:
                lines.append(f"- {c['message']}")
            lines.append("")

    lines.extend([
        "## Summary",
        "",
        f"- Total changes: {len(changes)}",
        f"- 🔴 Critical: {len(critical)}",
        f"- 🟡 Warning: {len(warnings)}",
        f"- 🔵 Info: {len(infos)}",
    ])

    return "\n".join(lines)


def build_result(old_schema_path, new_schema_path, changes):
    critical = [c for c in changes if c.get("severity") == "critical"]
    warnings = [c for c in changes if c.get("severity") == "warning"]
    infos = [c for c in changes if c.get("severity") == "info"]

    return {
        "breaking_changes_detected": bool(changes),
        "summary": {
            "total_changes": len(changes),
            "critical": len(critical),
            "warning": len(warnings),
            "info": len(infos),
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
    try:
        old_schema = load_openapi_file(old_schema_path)
        new_schema = load_openapi_file(new_schema_path)
    except Exception as e:
        print(f"❌ Error loading schema: {e}")
        sys.exit(1)

    changes = detect_breaking_changes(old_schema, new_schema)
    return changes


def print_usage():
    print("Usage:")
    print(
        "schemawatch <old_schema.yaml> <new_schema.yaml> "
        "[--format text|json|markdown] [--output result.json] [--quiet]"
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
                print("Error: --format requires a value (text, json or markdown)")
                sys.exit(1)
            output_format = args[i + 1].lower()
            if output_format not in {"text", "json", "markdown"}:
                print("Error: --format must be 'text', 'json' or 'markdown'")
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
    elif output_format == "markdown":
        content = format_markdown_output(changes)
    else:
        content = format_text_output(changes)

    if output_file:
        write_output_file(output_file, content)

    if not quiet:
        print(content)

    sys.exit(1 if changes else 0)


if __name__ == "__main__":
    main()