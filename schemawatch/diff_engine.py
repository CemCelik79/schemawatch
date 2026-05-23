from typing import Dict, Any, List


def make_change(message: str, severity: str = "warning"):
    return {
        "severity": severity,  # critical / warning / info
        "message": message,
    }


def get_schemas(schema: Dict[str, Any]):
    return schema.get("components", {}).get("schemas", {})


def compare_properties(schema_name, old_props, new_props, path=""):
    changes = []

    old_fields = set(old_props.keys())
    new_fields = set(new_props.keys())

    # Removed fields → warning
    for field in old_fields - new_fields:
        changes.append(
            make_change(f"Response field removed: {schema_name}.{path}{field}", "warning")
        )

    # Common fields
    for field in old_fields & new_fields:
        old_field = old_props[field]
        new_field = new_props[field]
        full_path = f"{path}{field}"

        old_type = get_type_repr(old_field)
        new_type = get_type_repr(new_field)

        if old_type != new_type:
            changes.append(
                make_change(
                    f"Field type changed: {schema_name}.{full_path} {old_type} -> {new_type}",
                    "warning"
                )
            )

        # Nested object
        if old_field.get("type") == "object" and new_field.get("type") == "object":
            old_nested = old_field.get("properties", {})
            new_nested = new_field.get("properties", {})
            changes.extend(
                compare_properties(schema_name, old_nested, new_nested, path=f"{full_path}.")
            )

        # Array item comparison → info
        if old_field.get("type") == "array" and new_field.get("type") == "array":
            old_items = old_field.get("items", {})
            new_items = new_field.get("items", {})
            if get_type_repr(old_items) != get_type_repr(new_items):
                changes.append(
                    make_change(
                        f"Array item type changed: {schema_name}.{full_path} array[{get_type_repr(old_items)}] -> array[{get_type_repr(new_items)}]",
                        "info"
                    )
                )

        # Enum comparison → info
        if "enum" in old_field and "enum" in new_field:
            if set(old_field["enum"]) != set(new_field["enum"]):
                changes.append(
                    make_change(
                        f"Enum changed: {schema_name}.{full_path} {old_field['enum']} -> {new_field['enum']}",
                        "info"
                    )
                )

    return changes


def get_type_repr(field):
    if "$ref" in field:
        return field["$ref"]
    if field.get("type") == "array":
        items = field.get("items", {})
        return f"array[{get_type_repr(items)}]"
    return field.get("type", "unknown")


def compare_schemas(old_schema, new_schema):
    changes = []

    old_schemas = get_schemas(old_schema)
    new_schemas = get_schemas(new_schema)

    old_names = set(old_schemas.keys())
    new_names = set(new_schemas.keys())

    # Removed schemas → critical
    for name in old_names - new_names:
        changes.append(make_change(f"Schema removed: {name}", "critical"))

    for name in old_names & new_names:
        old_props = old_schemas[name].get("properties", {})
        new_props = new_schemas[name].get("properties", {})
        changes.extend(compare_properties(name, old_props, new_props))

        # Required fields → warning
        old_req = set(old_schemas[name].get("required", []))
        new_req = set(new_schemas[name].get("required", []))
        for field in new_req - old_req:
            changes.append(make_change(f"Field became required: {name}.{field}", "warning"))

    return changes


def compare_paths(old_schema, new_schema):
    changes = []

    old_paths = old_schema.get("paths", {})
    new_paths = new_schema.get("paths", {})

    # Removed endpoints → critical
    for path in set(old_paths) - set(new_paths):
        changes.append(make_change(f"Endpoint removed: {path}", "critical"))

    # Removed methods → critical
    for path in set(old_paths) & set(new_paths):
        old_methods = set(old_paths[path].keys())
        new_methods = set(new_paths[path].keys())
        for method in old_methods - new_methods:
            changes.append(make_change(f"Method removed: {method.upper()} {path}", "critical"))

    return changes


HTTP_METHODS = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "trace"}
)


def _is_http_method(key: str) -> bool:
    return key.lower() in HTTP_METHODS


def _get_content_schema(part: Dict[str, Any]) -> Dict[str, Any]:
    content = part.get("content") or {}
    if not content:
        return {}
    if "application/json" in content:
        return content["application/json"].get("schema") or {}
    first = next(iter(content.values()), {})
    return first.get("schema") or {}


def _operation_label(method: str, path: str) -> str:
    return f"{method.upper()} {path}"


def _diff_body_properties(
    context: str,
    label: str,
    old_schema: Dict[str, Any],
    new_schema: Dict[str, Any],
) -> List:
    changes: List = []
    old_props = old_schema.get("properties") or {}
    new_props = new_schema.get("properties") or {}

    if context == "request":
        removed_prefix = "Request body field removed"
        type_prefix = "Request body field type changed"
    else:
        removed_prefix = "Response body field removed"
        type_prefix = "Response body field type changed"

    old_fields = set(old_props.keys())
    new_fields = set(new_props.keys())

    for field in old_fields - new_fields:
        changes.append(
            make_change(f"{removed_prefix}: {label}.{field}", "warning")
        )

    for field in old_fields & new_fields:
        old_field = old_props[field]
        new_field = new_props[field]
        old_type = get_type_repr(old_field)
        new_type = get_type_repr(new_field)
        if old_type != new_type:
            changes.append(
                make_change(
                    f"{type_prefix}: {label}.{field} {old_type} -> {new_type}",
                    "warning",
                )
            )
        if (
            old_field.get("type") == "object"
            and new_field.get("type") == "object"
        ):
            changes.extend(
                _diff_body_properties(
                    context,
                    f"{label}.{field}",
                    old_field,
                    new_field,
                )
            )

    return changes


def compare_operations(old_schema, new_schema):
    changes: List = []
    old_paths = old_schema.get("paths") or {}
    new_paths = new_schema.get("paths") or {}

    for path in set(old_paths) & set(new_paths):
        old_item = old_paths[path]
        new_item = new_paths[path]
        old_methods = {m for m in old_item if _is_http_method(m)}
        new_methods = {m for m in new_item if _is_http_method(m)}

        for method in old_methods & new_methods:
            old_op = old_item[method]
            new_op = new_item[method]
            op_label = _operation_label(method, path)

            old_rb = old_op.get("requestBody")
            new_rb = new_op.get("requestBody")

            if old_rb and not new_rb:
                changes.append(
                    make_change(f"Request body removed: {op_label}", "critical")
                )
            elif old_rb and new_rb:
                if not old_rb.get("required", False) and new_rb.get("required", False):
                    changes.append(
                        make_change(
                            f"Request body became required: {op_label}",
                            "warning",
                        )
                    )
                changes.extend(
                    _diff_body_properties(
                        "request",
                        op_label,
                        _get_content_schema(old_rb),
                        _get_content_schema(new_rb),
                    )
                )

            old_responses = old_op.get("responses") or {}
            new_responses = new_op.get("responses") or {}

            for status in set(old_responses) - set(new_responses):
                changes.append(
                    make_change(
                        f"Response status code removed: {status} {op_label}",
                        "critical",
                    )
                )

            for status in set(old_responses) & set(new_responses):
                old_resp = old_responses[status]
                new_resp = new_responses[status]
                resp_label = f"{op_label} {status}"
                changes.extend(
                    _diff_body_properties(
                        "response",
                        resp_label,
                        _get_content_schema(old_resp),
                        _get_content_schema(new_resp),
                    )
                )

    return changes


def detect_breaking_changes(old_schema, new_schema):
    changes = []
    changes.extend(compare_paths(old_schema, new_schema))
    changes.extend(compare_operations(old_schema, new_schema))
    changes.extend(compare_schemas(old_schema, new_schema))
    return changes