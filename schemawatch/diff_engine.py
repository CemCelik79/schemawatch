from typing import Dict, Any, List


def make_change(message: str):
    return {
        "level": "breaking",
        "message": message,
    }


def get_schemas(schema: Dict[str, Any]):
    return schema.get("components", {}).get("schemas", {})


def compare_properties(schema_name, old_props, new_props, path=""):
    changes = []

    old_fields = set(old_props.keys())
    new_fields = set(new_props.keys())

    # Removed fields
    for field in old_fields - new_fields:
        changes.append(
            make_change(f"Response field removed: {schema_name}.{path}{field}")
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
                    f"Field type changed: {schema_name}.{full_path} {old_type} -> {new_type}"
                )
            )

        # Recursive check for nested object
        if old_field.get("type") == "object" and new_field.get("type") == "object":
            old_nested = old_field.get("properties", {})
            new_nested = new_field.get("properties", {})

            changes.extend(
                compare_properties(schema_name, old_nested, new_nested, path=f"{full_path}.")
            )

        # Array item comparison
        if old_field.get("type") == "array" and new_field.get("type") == "array":
            old_items = old_field.get("items", {})
            new_items = new_field.get("items", {})

            if get_type_repr(old_items) != get_type_repr(new_items):
                changes.append(
                    make_change(
                        f"Field type changed: {schema_name}.{full_path} array[{get_type_repr(old_items)}] -> array[{get_type_repr(new_items)}]"
                    )
                )

        # Enum comparison
        if "enum" in old_field and "enum" in new_field:
            if set(old_field["enum"]) != set(new_field["enum"]):
                changes.append(
                    make_change(
                        f"Enum changed: {schema_name}.{full_path} {old_field['enum']} -> {new_field['enum']}"
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

    # Removed schemas
    for name in old_names - new_names:
        changes.append(make_change(f"Schema removed: {name}"))

    # Compare common schemas
    for name in old_names & new_names:
        old_props = old_schemas[name].get("properties", {})
        new_props = new_schemas[name].get("properties", {})

        changes.extend(compare_properties(name, old_props, new_props))

        # Required fields
        old_req = set(old_schemas[name].get("required", []))
        new_req = set(new_schemas[name].get("required", []))

        for field in new_req - old_req:
            changes.append(make_change(f"Field became required: {name}.{field}"))

    return changes


def compare_paths(old_schema, new_schema):
    changes = []

    old_paths = old_schema.get("paths", {})
    new_paths = new_schema.get("paths", {})

    # Removed endpoints
    for path in set(old_paths) - set(new_paths):
        changes.append(make_change(f"Endpoint removed: {path}"))

    # Method comparison
    for path in set(old_paths) & set(new_paths):
        old_methods = set(old_paths[path].keys())
        new_methods = set(new_paths[path].keys())

        for method in old_methods - new_methods:
            changes.append(make_change(f"Method removed: {method.upper()} {path}"))

    return changes


def detect_breaking_changes(old_schema, new_schema):
    changes = []

    changes.extend(compare_paths(old_schema, new_schema))
    changes.extend(compare_schemas(old_schema, new_schema))

    return changes