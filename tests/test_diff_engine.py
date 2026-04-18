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


def test_detects_removed_field_in_any_schema():
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


def test_detects_field_type_change():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
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
                    },
                }
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field type changed: User.id integer -> string" in messages


def test_detects_field_became_required():
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


def test_detects_changes_in_multiple_schemas():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                    },
                },
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "status": {"type": "string"},
                    },
                },
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
                    },
                },
                "Order": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                    },
                },
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert "Field type changed: User.id integer -> string" in messages
    assert "Response field removed: User.email" in messages
    assert "Response field removed: Order.status" in messages


def test_supports_ref_field_type_comparison():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "Profile": {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer"},
                    },
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "profile": {"$ref": "#/components/schemas/Profile"},
                    },
                },
            }
        },
    }
    new_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "ProfileV2": {
                    "type": "object",
                    "properties": {
                        "age": {"type": "integer"},
                    },
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "profile": {"$ref": "#/components/schemas/ProfileV2"},
                    },
                },
            }
        },
    }

    changes = detect_breaking_changes(old_schema, new_schema)
    messages = get_messages(changes)

    assert (
        "Field type changed: User.profile #/components/schemas/Profile -> #/components/schemas/ProfileV2"
        in messages
    )


def test_returns_empty_when_no_breaking_changes():
    schema = {
        "paths": {
            "/users": {"get": {}, "post": {}},
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "email": {"type": "string"},
                    },
                    "required": ["id"],
                }
            }
        },
    }

    changes = detect_breaking_changes(schema, schema)
    assert changes == []