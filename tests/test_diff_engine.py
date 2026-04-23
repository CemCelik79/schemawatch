from schemawatch.diff_engine import detect_breaking_changes


def get_messages(changes):
    return [change["message"] for change in changes]


def test_detects_removed_endpoint():
    old_schema = {
        "paths": {
            "/users": {"get": {}},
            "/orders": {"post": {}},
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/users": {"get": {}},
        },
        "components": {"schemas": {}},
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Endpoint removed: /orders" in messages


def test_detects_removed_method():
    old_schema = {
        "paths": {
            "/users": {"get": {}, "post": {}},
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/users": {"post": {}},
        },
        "components": {"schemas": {}},
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Method removed: GET /users" in messages


def test_detects_removed_schema():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {"type": "object", "properties": {}},
                "Order": {"type": "object", "properties": {}},
            }
        },
    }
    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {"type": "object", "properties": {}},
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Schema removed: Order" in messages


def test_detects_removed_field():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "total": {"type": "number"},
                    },
                }
            }
        },
    }
    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Response field removed: Order.total" in messages


def test_field_type_change():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "properties": {"id": {"type": "integer"}},
                }
            }
        },
    }
    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "properties": {"id": {"type": "string"}},
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field type changed: User.id integer -> string" in messages


def test_field_became_required():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "properties": {"id": {"type": "integer"}},
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
                    "properties": {"id": {"type": "integer"}},
                    "required": ["id"],
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field became required: User.id" in messages


# --- Yeni testler ---

def test_array_item_type_change():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "properties": {
                        "ids": {"type": "array", "items": {"type": "integer"}}
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
                    "properties": {
                        "ids": {"type": "array", "items": {"type": "string"}}
                    }
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert any("User.ids" in m for m in messages)


def test_empty_schema():
    old_schema = {"paths": {}, "components": {"schemas": {}}}
    new_schema = {"paths": {}, "components": {"schemas": {}}}

    changes = detect_breaking_changes(old_schema, new_schema)
    assert changes == []


def test_missing_components():
    old_schema = {"paths": {}}
    new_schema = {"paths": {}}

    changes = detect_breaking_changes(old_schema, new_schema)
    assert changes == []


def test_nested_object_field_removed():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "age": {"type": "integer"},
                                "city": {"type": "string"},
                            },
                        }
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
                    "properties": {
                        "profile": {
                            "type": "object",
                            "properties": {
                                "age": {"type": "integer"},
                            },
                        }
                    }
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert isinstance(messages, list)