# Agentic AI with RBAC

An interview-friendly FastAPI demo that shows a key security principle for AI agents: **the model proposes actions, but deterministic policy code decides whether they may run**.

The API accepts a natural-language task, produces a small agent plan, and executes only tools authorized for the authenticated user's role. The project works out of the box with a deterministic planner; an optional OpenAI planner can be added later without changing the authorization boundary.

## What it demonstrates

- Role-based access control: `viewer`, `analyst`, and `admin`
- Tool-level permission checks before every agent action
- Explicit denial events in an audit log
- A planner/executor split, so an LLM cannot grant itself permissions
- A lightweight in-memory data store to keep the demo easy to run

## Quick start

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for Swagger UI.

## Try it

The demo uses the `X-User-Id` header as a deliberately simple development authentication mechanism.

```powershell
# Viewer: allowed to read a report
Invoke-RestMethod http://127.0.0.1:8000/agent/run -Method POST -Headers @{"X-User-Id"="alice"} -ContentType "application/json" -Body '{"task":"show the quarterly report"}'

# Viewer: blocked from inviting a user
Invoke-RestMethod http://127.0.0.1:8000/agent/run -Method POST -Headers @{"X-User-Id"="alice"} -ContentType "application/json" -Body '{"task":"invite sam@example.com as an analyst"}'

# Admin: allowed to invite a user
Invoke-RestMethod http://127.0.0.1:8000/agent/run -Method POST -Headers @{"X-User-Id"="carol"} -ContentType "application/json" -Body '{"task":"invite sam@example.com as an analyst"}'
```

Seed users: `alice` (viewer), `bob` (analyst), `carol` (admin).

## Architecture

```text
User task -> Planner -> Proposed tool calls -> RBAC policy -> Tool executor
                                           |                  |
                                           +-> Audit log <----+
```

The planner is intentionally untrusted. It may request `invite_user`, but only the policy layer can authorize that tool. In a production service, replace the header with OIDC/JWT authentication, persist users/audit records, and enforce tenant/data-scoping in addition to role permissions.

## Test

```powershell
pytest -q
```
