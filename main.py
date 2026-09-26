from fastapi import FastAPI, Header, HTTPException

from app.agent import execute, plan
from app.models import AgentRequest, AgentResponse, AuditEvent, Role, StepResult, ToolName, User
from app.policy import ROLE_PERMISSIONS, is_allowed

app = FastAPI(title="Agentic AI with RBAC", version="1.0.0")

USERS = {
    "alice": User(id="alice", name="Alice Viewer", role=Role.VIEWER),
    "bob": User(id="bob", name="Bob Analyst", role=Role.ANALYST),
    "carol": User(id="carol", name="Carol Admin", role=Role.ADMIN),
}
AUDIT_LOG: list[AuditEvent] = []


def current_user(x_user_id: str | None) -> User:
    user = USERS.get(x_user_id or "")
    if not user:
        raise HTTPException(status_code=401, detail="Provide a valid X-User-Id header.")
    return user


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/me")
def me(x_user_id: str | None = Header(default=None)) -> User:
    return current_user(x_user_id)


@app.get("/roles")
def roles() -> dict[str, list[str]]:
    return {role.value: sorted(tool.value for tool in tools) for role, tools in ROLE_PERMISSIONS.items()}


@app.get("/audit", response_model=list[AuditEvent])
def audit(x_user_id: str | None = Header(default=None)) -> list[AuditEvent]:
    user = current_user(x_user_id)
    if user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can view the audit log.")
    return AUDIT_LOG


@app.post("/agent/run", response_model=AgentResponse)
def run_agent(request: AgentRequest, x_user_id: str | None = Header(default=None)) -> AgentResponse:
    user = current_user(x_user_id)
    results: list[StepResult] = []

    for call in plan(request.task):
        allowed = is_allowed(user.role, call.tool)
        if allowed:
            detail = execute(call)
            status = "executed"
        else:
            detail = f"Denied: role '{user.role.value}' cannot execute '{call.tool.value}'."
            status = "denied"

        AUDIT_LOG.append(AuditEvent(user_id=user.id, role=user.role, tool=call.tool, allowed=allowed, detail=detail))
        results.append(StepResult(tool=call.tool, status=status, detail=detail))

    return AgentResponse(user=user.name, role=user.role, task=request.task, steps=results)
