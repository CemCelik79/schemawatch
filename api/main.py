from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlmodel import SQLModel, Field, Session, create_engine, select
from sqlalchemy import Column
from sqlalchemy.types import JSON


# -----------------------------
# App
# -----------------------------
app = FastAPI(title="SchemaWatch API")


# -----------------------------
# Database
# -----------------------------
sqlite_file_name = "schemawatch.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)


# -----------------------------
# Database Model
# -----------------------------
class SchemaRecord(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    schema: Dict = Field(sa_column=Column(JSON))


# -----------------------------
# Request Models
# -----------------------------
class SchemaCreateRequest(BaseModel):
    name: str
    schema: Dict


class CompareRequest(BaseModel):
    old_schema_id: int
    new_schema_id: int


# -----------------------------
# Response Models
# -----------------------------
class CompareResponse(BaseModel):
    changes: List[str]


class DiffResponse(BaseModel):
    added: List[str]
    removed: List[str]
    changed: List[str]


# -----------------------------
# Startup
# -----------------------------
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)


# -----------------------------
# Helper Functions
# -----------------------------
def get_schema_or_404(schema_id: int) -> SchemaRecord:
    with Session(engine) as session:
        schema_record = session.get(SchemaRecord, schema_id)
        if not schema_record:
            raise HTTPException(
                status_code=404,
                detail=f"Schema with id={schema_id} not found"
            )
        return schema_record


def calculate_diff(old_schema: Dict, new_schema: Dict):
    old_keys = set(old_schema.keys())
    new_keys = set(new_schema.keys())

    added = sorted(list(new_keys - old_keys))
    removed = sorted(list(old_keys - new_keys))

    common_keys = old_keys.intersection(new_keys)
    changed = sorted([
        key for key in common_keys
        if old_schema[key] != new_schema[key]
    ])

    return added, removed, changed


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def root():
    return {"message": "SchemaWatch API is running 🚀"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/schemas")
def create_schema(payload: SchemaCreateRequest):
    with Session(engine) as session:
        new_schema = SchemaRecord(
            name=payload.name,
            schema=payload.schema
        )
        session.add(new_schema)
        session.commit()
        session.refresh(new_schema)
        return new_schema


@app.get("/schemas")
def list_schemas():
    with Session(engine) as session:
        schemas = session.exec(select(SchemaRecord)).all()
        return schemas


@app.get("/schemas/{schema_id}")
def get_schema(schema_id: int):
    return get_schema_or_404(schema_id)


@app.post("/compare", response_model=CompareResponse)
def compare_schemas(payload: CompareRequest):
    old_record = get_schema_or_404(payload.old_schema_id)
    new_record = get_schema_or_404(payload.new_schema_id)

    added, removed, changed = calculate_diff(old_record.schema, new_record.schema)

    changes = []

    for field in added:
        changes.append(f"Added field: {field}")

    for field in removed:
        changes.append(f"Removed field: {field}")

    for field in changed:
        changes.append(
            f"Changed field type: {field} ({old_record.schema[field]} -> {new_record.schema[field]})"
        )

    return {"changes": changes}


@app.post("/diff", response_model=DiffResponse)
def diff_schemas(payload: CompareRequest):
    old_record = get_schema_or_404(payload.old_schema_id)
    new_record = get_schema_or_404(payload.new_schema_id)

    added, removed, changed = calculate_diff(old_record.schema, new_record.schema)

    return {
        "added": added,
        "removed": removed,
        "changed": changed
    }