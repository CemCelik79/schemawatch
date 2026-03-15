def extract_path_methods(schema):
    paths = schema.get("paths", {})
    result = {}

    for path, path_item in paths.items():
        if isinstance(path_item, dict):
            methods = set()

            for method_name in path_item.keys():
                if method_name.lower() in {
                    "get",
                    "post",
                    "put",
                    "delete",
                    "patch",
                    "options",
                    "head",
                }:
                    methods.add(method_name.upper())

            result[path] = methods

    return result


def extract_schema_definition(schema, schema_name):
    components = schema.get("components", {})
    schemas = components.get("schemas", {})
    return schemas.get(schema_name, {})


def extract_schema_properties(schema, schema_name):
    target = extract_schema_definition(schema, schema_name)
    return target.get("properties", {})


def extract_required_fields(schema, schema_name):
    target = extract_schema_definition(schema, schema_name)
    required = target.get("required", [])
    return set(required)


def make_change(code, level, message):
    return {
        "code": code,
        "level": level,
        "message": message,
    }


def detect_breaking_changes(old_schema, new_schema):
    changes = []

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

    old_props = extract_schema_properties(old_schema, "User")
    new_props = extract_schema_properties(new_schema, "User")

    old_fields = set(old_props.keys())
    new_fields = set(new_props.keys())

    removed_fields = old_fields - new_fields
    for field in sorted(removed_fields):
        changes.append(
            make_change(
                "field_removed",
                "breaking",
                f"Response field removed: User.{field}",
            )
        )

    common_fields = old_fields & new_fields
    for field in sorted(common_fields):
        old_type = old_props[field].get("type")
        new_type = new_props[field].get("type")

        if old_type != new_type:
            changes.append(
                make_change(
                    "field_type_changed",
                    "breaking",
                    f"Field type changed: User.{field} {old_type} -> {new_type}",
                )
            )

    old_required = extract_required_fields(old_schema, "User")
    new_required = extract_required_fields(new_schema, "User")

    newly_required = new_required - old_required
    for field in sorted(newly_required):
        changes.append(
            make_change(
                "field_became_required",
                "breaking",
                f"Field became required: User.{field}",
            )
        )

    return changes