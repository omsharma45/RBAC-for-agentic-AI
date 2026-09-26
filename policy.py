from app.models import Role, ToolName


ROLE_PERMISSIONS: dict[Role, set[ToolName]] = {
    Role.VIEWER: {ToolName.READ_REPORT, ToolName.SEARCH_KNOWLEDGE_BASE},
    Role.ANALYST: {
        ToolName.READ_REPORT,
        ToolName.SEARCH_KNOWLEDGE_BASE,
        ToolName.EXPORT_REPORT,
    },
    Role.ADMIN: set(ToolName),
}


def is_allowed(role: Role, tool: ToolName) -> bool:
    """Return whether a role is authorized to execute a specific agent tool."""
    return tool in ROLE_PERMISSIONS[role]
