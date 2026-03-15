from schemawatch.diff_engine import detect_breaking_changes


def get_messages(changes):
    return [change["message"] for change in changes]


def test_detects_method_removed():
    old_schema = {
        "paths": {
            "/users": {
                "get": {},
                "post": {},
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                    }
                }
            }
        },
    }

    new_schema = {
        "paths": {
            "/users": {
                "post": {},
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                    }
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Method removed: GET /users" in messages


def test_detects_removed_field():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                    }
                }
            }
        },
    }

    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    }
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Response field removed: User.email" in messages


def test_detects_type_change():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    }
                }
            }
        },
    }

    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                    }
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field type changed: User.id integer -> string" in messages


def test_detects_newly_required_field():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
                    "required": [],
                }
            }
        },
    }

    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
                    "required": ["id"],
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field became required: User.id" in messages