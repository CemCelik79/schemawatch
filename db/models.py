from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field


class SchemaRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str
    source: str
    schema_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class DiffRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    project_name: str
    old_schema_id: int
    new_schema_id: int
    changes_json: str
    created_at: datetime = Field(default_factory=datetime.utcnow)