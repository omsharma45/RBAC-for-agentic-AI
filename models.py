from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    VIEWER = "viewer"
    ANALYST = "analyst"
    ADMIN = "admin"


class ToolName(StrEnum):
    READ_REPORT = "read_report"
    SEARCH_KNOWLEDGE_BASE = "search_knowledge_base"
    EXPORT_REPORT = "export_report"
    INVITE_USER = "invite_user"
    DELETE_REPORT = "delete_report"


class User(BaseModel):
    id: str
    name: str
    role: Role


class AgentRequest(BaseModel):
    task: str = Field(min_length=3, max_length=500)


class ToolCall(BaseModel):
    tool: ToolName
    arguments: dict[str, str] = Field(default_factory=dict)
    rationale: str


class StepResult(BaseModel):
    tool: ToolName
    status: str
    detail: str


class AgentResponse(BaseModel):
    user: str
    role: Role
    task: str
    steps: list[StepResult]


class AuditEvent(BaseModel):
    user_id: str
    role: Role
    tool: ToolName
    allowed: bool
    detail: str
