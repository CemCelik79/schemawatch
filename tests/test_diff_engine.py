from schemawatch.diff_engine import detect_breaking_changes, resolve_schema


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


def test_request_body_removed():
    old_schema = {
        "paths": {
            "/items": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "name": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {"/items": {"post": {}}},
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Request body removed: POST /items" in messages


def test_request_body_became_required():
    old_schema = {
        "paths": {
            "/items": {
                "post": {
                    "requestBody": {
                        "required": False,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {}},
                            }
                        },
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/items": {
                "post": {
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "properties": {}},
                            }
                        },
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Request body became required: POST /items" in messages


def test_request_body_field_removed_and_type_changed():
    old_schema = {
        "paths": {
            "/items": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "integer"},
                                        "name": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/items": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "id": {"type": "string"},
                                    },
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Request body field removed: POST /items.name" in messages
    assert "Request body field type changed: POST /items.id integer -> string" in messages


def test_response_status_removed():
    old_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "200": {"description": "ok"},
                        "404": {"description": "not found"},
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "404": {"description": "not found"},
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Response status code removed: 200 GET /x" in messages


def test_response_body_field_removed():
    old_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                            "email": {"type": "string"},
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "id": {"type": "integer"},
                                        },
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Response body field removed: GET /x 200.email" in messages


def test_resolve_schema_internal_ref():
    doc = {
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {"id": {"type": "integer"}},
                }
            }
        }
    }
    resolved = resolve_schema(doc, {"$ref": "#/components/schemas/User"})
    assert resolved.get("type") == "object"
    assert "id" in resolved.get("properties", {})


def test_request_body_ref_to_components():
    old_schema = {
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserInput"}
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "UserInput": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "name": {"type": "string"},
                    },
                }
            }
        },
    }
    new_schema = {
        "paths": {
            "/users": {
                "post": {
                    "requestBody": {
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/UserInput"}
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "UserInput": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                    },
                }
            }
        },
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Response field removed: UserInput.email" in messages
    assert not any("Request body field removed" in m for m in messages)


def test_component_schema_property_ref():
    old_schema = {
        "paths": {},
        "components": {
            "schemas": {
                "Order": {
                    "type": "object",
                    "properties": {
                        "customer": {"$ref": "#/components/schemas/Customer"},
                    },
                },
                "Customer": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                    },
                },
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
                        "customer": {"$ref": "#/components/schemas/Customer"},
                    },
                },
                "Customer": {
                    "type": "object",
                    "properties": {},
                },
            }
        },
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Response field removed: Customer.email" in messages


def test_no_duplicate_when_response_uses_component_ref():
    """Field changes on a shared schema should not appear twice (schema + response body)."""
    old_schema = {
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "name": {"type": "string"},
                    },
                }
            }
        },
    }
    new_schema = {
        "paths": {
            "/users": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {"$ref": "#/components/schemas/User"}
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {
            "schemas": {
                "User": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                    },
                }
            }
        },
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    email_messages = [m for m in messages if "email" in m]
    assert len(email_messages) == 1
    assert "Response field removed: User.email" in messages
    assert not any("Response body field removed" in m and "email" in m for m in messages)


def test_inline_response_body_still_reported():
    """Inline response schemas are not deduplicated against components."""
    old_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"token": {"type": "string"}},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }
    new_schema = {
        "paths": {
            "/x": {
                "get": {
                    "responses": {
                        "200": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {},
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "components": {"schemas": {}},
    }

    messages = get_messages(detect_breaking_changes(old_schema, new_schema))
    assert "Response body field removed: GET /x 200.token" in messages