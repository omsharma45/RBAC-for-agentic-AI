import re

from app.models import ToolCall, ToolName


def plan(task: str) -> list[ToolCall]:
    """Create deterministic, inspectable tool proposals for this demo.

    In a production system, an LLM may create these proposals. The executor must
    still treat the output as untrusted and validate each proposed tool call.
    """
    lower_task = task.lower()
    calls: list[ToolCall] = []

    if any(word in lower_task for word in ("report", "quarterly", "revenue")):
        calls.append(ToolCall(tool=ToolName.READ_REPORT, rationale="The task requests report data."))
    if any(word in lower_task for word in ("search", "policy", "knowledge base", "how do")):
        calls.append(ToolCall(tool=ToolName.SEARCH_KNOWLEDGE_BASE, rationale="The task requests internal information."))
    if any(word in lower_task for word in ("export", "download", "csv")):
        calls.append(ToolCall(tool=ToolName.EXPORT_REPORT, rationale="The task asks for an export."))
    if any(word in lower_task for word in ("invite", "add user", "create user")):
        email = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", task)
        calls.append(
            ToolCall(
                tool=ToolName.INVITE_USER,
                arguments={"email": email.group(0) if email else "new.user@example.com"},
                rationale="The task asks to provision a user.",
            )
        )
    if any(word in lower_task for word in ("delete", "remove", "destroy")):
        calls.append(ToolCall(tool=ToolName.DELETE_REPORT, rationale="The task requests destructive deletion."))

    if not calls:
        calls.append(ToolCall(tool=ToolName.SEARCH_KNOWLEDGE_BASE, rationale="Use safe search for a general question."))
    return calls


def execute(call: ToolCall) -> str:
    """Mock integrations. Keep side effects here, behind the policy boundary."""
    outcomes = {
        ToolName.READ_REPORT: "Quarterly report: revenue $1.24M; customer growth 12%.",
        ToolName.SEARCH_KNOWLEDGE_BASE: "Knowledge base search completed; found onboarding and reporting guidance.",
        ToolName.EXPORT_REPORT: "Created secure download link: /exports/quarterly-report.csv",
        ToolName.INVITE_USER: f"Invitation queued for {call.arguments.get('email', 'new user')}.",
        ToolName.DELETE_REPORT: "Quarterly report marked for deletion.",
    }
    return outcomes[call.tool]
