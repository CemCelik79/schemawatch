from fastapi import FastAPI
from pydantic import BaseModel
from sqlmodel import Session
from db.database import engine
from db.models import SchemaRecord
import json
from db.models import DiffRun

from db.database import create_db_and_tables
from schemawatch.diff_engine import detect_breaking_changes

app = FastAPI()


class DiffRequest(BaseModel):
    old_schema: dict
    new_schema: dict
class SchemaCreateRequest(BaseModel):
    project_name: str
    source: str
    schema: dict
class CompareRequest(BaseModel):
    old_schema_id: int
    new_schema_id: int


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/")
def root():
    return {"message": "SchemaWatch API is running"}


@app.post("/diff")
def diff_schemas(request: DiffRequest):
    changes = detect_breaking_changes(
        request.old_schema,
        request.new_schema
    )

    return {"changes": changes}
@app.post("/schemas")
def create_schema(request: SchemaCreateRequest):

    schema_record = SchemaRecord(
        project_name=request.project_name,
        source=request.source,
        schema_json=json.dumps(request.schema)
    )

    with Session(engine) as session:
        session.add(schema_record)
        session.commit()
        session.refresh(schema_record)

    return {
        "schema_id": schema_record.id
    }

@app.post("/compare")
def compare_schemas(request: CompareRequest):

    with Session(engine) as session:

        old_schema = session.get(SchemaRecord, request.old_schema_id)
        new_schema = session.get(SchemaRecord, request.new_schema_id)

        old_schema_json = json.loads(old_schema.schema_json)
        new_schema_json = json.loads(new_schema.schema_json)

        changes = detect_breaking_changes(
            old_schema_json,
            new_schema_json
        )

        diff_run = DiffRun(
            project_name=old_schema.project_name,
            old_schema_id=request.old_schema_id,
            new_schema_id=request.new_schema_id,
            changes_json=json.dumps(changes)
        )

        session.add(diff_run)
        session.commit()

    return {
        "changes": changes
    }