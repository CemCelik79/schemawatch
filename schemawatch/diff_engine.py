from __future__ import annotations

from typing import Any, Dict, List, Set, Tuple


HTTP_METHODS = {"get", "post", "put", "delete", "patch", "options", "head", "trace"}


def make_change(code: str, level: str, message: str) -> Dict[str, str]:
    return {
        "code": code,
        "level": level,
        "message": message,
    }


def extract_path_methods(schema: Dict[str, Any]) -> Dict[str, Set[str]]:
    paths = schema.get("paths", {})
    result: Dict[str, Set[str]] = {}

    if not isinstance(paths, dict):
        return result

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        methods = {
            method_name.upper()
            for method_name in path_item.keys()
            if isinstance(method_name, str) and method_name.lower() in HTTP_METHODS
        }

        result[path] = methods

    return result


def get_component_schemas(schema: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    components = schema.get("components", {})
    if not isinstance(components, dict):
        return {}

    schemas = components.get("schemas", {})
    if not isinstance(schemas, dict):
        return {}

    return {name: value for name, value in schemas.items() if isinstance(value, dict)}


def resolve_schema_ref(
    openapi_schema: Dict[str, Any],
    schema_or_ref: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Supports local refs like:
    #/components/schemas/User
    """
    if not isinstance(schema_or_ref, dict):
        return {}

    ref = schema_or_ref.get("$ref")
    if not ref:
        return schema_or_ref

    if not isinstance(ref, str):
        return {}

    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        return {}

    schema_name = ref[len(prefix):]
    return get_component_schemas(openapi_schema).get(schema_name, {})


def extract_object_properties(
    openapi_schema: Dict[str, Any],
    schema_def: Dict[str, Any],
) -> Dict[str, Dict[str, Any]]:
    schema_def = resolve_schema_ref(openapi_schema, schema_def)

    properties = schema_def.get("properties", {})
    if not isinstance(properties, dict):
        return {}

    return {name: value for name, value in properties.items() if isinstance(value, dict)}


def extract_required_fields(
    openapi_schema: Dict[str, Any],
    schema_def: Dict[str, Any],
) -> Set[str]:
    schema_def = resolve_schema_ref(openapi_schema, schema_def)

    required = schema_def.get("required", [])
    if not isinstance(required, list):
        return set()

    return {item for item in required if isinstance(item, str)}


def field_type_repr(openapi_schema: Dict[str, Any], field_schema: Dict[str, Any]) -> str:
    field_schema = resolve_schema_ref(openapi_schema, field_schema)

    if "$ref" in field_schema:
        return field_schema["$ref"]

    schema_type = field_schema.get("type")
    schema_format = field_schema.get("format")

    if schema_type and schema_format:
        return f"{schema_type}:{schema_format}"

    if schema_type:
        return str(schema_type)

    if "oneOf" in field_schema:
        return "oneOf"

    if "anyOf" in field_schema:
        return "anyOf"

    if "allOf" in field_schema:
        return "allOf"

    return "unknown"


def compare_paths(old_schema: Dict[str, Any], new_schema: Dict[str, Any]) -> List[Dict[str, str]]:
    changes: List[Dict[str, str]] = []

    old_path_methods = extract_path_methods(old_schema)
    new_path_methods = extract_path_methods(new_schema)

    old_paths = set(old_path_methods.keys())
    new_paths = set(new_path_methods.keys())

    removed_paths = old_paths - new_paths
    for path in sorted(removed_paths):
        changes.append(
            make_change(
                "endpoint_removed",
                "breaking",
                f"Endpoint removed: {path}",
            )
        )

    common_paths = old_paths & new_paths
    for path in sorted(common_paths):
        old_methods = old_path_methods[path]
        new_methods = new_path_methods[path]

        removed_methods = old_methods - new_methods
        for method in sorted(removed_methods):
            changes.append(
                make_change(
                    "method_removed",
                    "breaking",
                    f"Method removed: {method} {path}",
                )
            )

    return changes


def compare_component_schemas(
    old_schema: Dict[str, Any],
    new_schema: Dict[str, Any],
) -> List[Dict[str, str]]:
    changes: List[Dict[str, str]] = []

    old_schemas = get_component_schemas(old_schema)
    new_schemas = get_component_schemas(new_schema)

    old_schema_names = set(old_schemas.keys())
    new_schema_names = set(new_schemas.keys())

    removed_schema_names = old_schema_names - new_schema_names
    for schema_name in sorted(removed_schema_names):
        changes.append(
            make_change(
                "schema_removed",
                "breaking",
                f"Schema removed: {schema_name}",
            )
        )

    common_schema_names = old_schema_names & new_schema_names

    for schema_name in sorted(common_schema_names):
        old_def = old_schemas[schema_name]
        new_def = new_schemas[schema_name]

        old_props = extract_object_properties(old_schema, old_def)
        new_props = extract_object_properties(new_schema, new_def)

        old_fields = set(old_props.keys())
        new_fields = set(new_props.keys())

        removed_fields = old_fields - new_fields
        for field in sorted(removed_fields):
            changes.append(
                make_change(
                    "field_removed",
                    "breaking",
                    f"Response field removed: {schema_name}.{field}",
                )
            )

        common_fields = old_fields & new_fields
        for field in sorted(common_fields):
            old_type = field_type_repr(old_schema, old_props[field])
            new_type = field_type_repr(new_schema, new_props[field])

            if old_type != new_type:
                changes.append(
                    make_change(
                        "field_type_changed",
                        "breaking",
                        f"Field type changed: {schema_name}.{field} {old_type} -> {new_type}",
                    )
                )

        old_required = extract_required_fields(old_schema, old_def)
        new_required = extract_required_fields(new_schema, new_def)

        newly_required = new_required - old_required
        for field in sorted(newly_required):
            changes.append(
                make_change(
                    "field_became_required",
                    "breaking",
                    f"Field became required: {schema_name}.{field}",
                )
            )

    return changes


def detect_breaking_changes(
    old_schema: Dict[str, Any],
    new_schema: Dict[str, Any],
) -> List[Dict[str, str]]:
    changes: List[Dict[str, str]] = []
    changes.extend(compare_paths(old_schema, new_schema))
    changes.extend(compare_component_schemas(old_schema, new_schema))
    return changes