from pydantic import BaseModel, Field, ValidationError
from enum import Enum
from typing import Dict, Any

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Task(BaseModel):
    name: str = Field(description="Name of the task")
    due_date: str = Field(description="Due date of the task in YYYY-MM-DD format (e.g., 2023-12-31)")
    priority: Priority = Field(description="Priority of the task (high, medium, low)")

    class Config:
        use_enum_values = True

# Helper to get JSON schema for re-prompting
def get_task_schema_json() -> Dict[str, Any]:
    return Task.model_json_schema()
