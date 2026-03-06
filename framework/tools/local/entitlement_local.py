"""
Entitlement tool — local implementation.

In production, replace _ENTITLEMENT_DB with a real IAM / LDAP / SailPoint
API call.  Swapping to an MCP implementation requires zero agent code changes
(just register "entitlement", "mcp", EntitlementMCPTools() in the registry).
"""
from core.schemas import EntitlementCheckResult
from framework.tools.base_tool import BaseTool
import logging

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mock entitlement database
# Key  : app_name (lower-cased)
# Value: dict mapping user_id → access_type  ("read" | "write" | "admin")
# ---------------------------------------------------------------------------
_ENTITLEMENT_DB: dict[str, dict[str, str]] = {
    "salesforce": {
        "alice": "write",
        "bob": "read",
        "carol": "admin",
        "svc_batch": "read",
    },
    "jira": {
        "alice": "write",
        "dave": "write",
        "eve": "read",
    },
    "confluence": {
        "alice": "read",
        "bob": "write",
        "carol": "read",
        "frank": "admin",
    },
}

# Accounts flagged as invalid / stale in the identity store
_INVALID_USERS = {"svc_batch", "ghost_user", "former_emp_john"}


class EntitlementLocalTools(BaseTool):
    """Day 1: checks entitlements from an in-memory mock DB.
    Day 2: replaced by EntitlementMCPTools — zero agent code changes."""

    name = "entitlement_tools"
    description = "Validates user entitlements for a given application"

    async def check_user_entitlements(
        self,
        app_name: str,
        users: list[str],
    ) -> list[EntitlementCheckResult]:
        """
        Check whether a list of users have access to the given application.

        Args:
            app_name: Name of the application to check (e.g. "Salesforce").
            users:    List of user IDs / usernames to validate.

        Returns:
            One EntitlementCheckResult per user with has_access, access_type,
            is_valid_user, and a plain-English reason.
        """
        app_key = app_name.lower()
        app_entitlements: dict[str, str] = _ENTITLEMENT_DB.get(app_key, {})
        logger.info(
            f"Checking {len(users)} users against '{app_name}' entitlements"
        )

        results: list[EntitlementCheckResult] = []
        for user_id in users:
            user_key = user_id.strip().lower()
            is_valid = user_key not in _INVALID_USERS
            access_type = app_entitlements.get(user_key)
            has_access = access_type is not None

            if not is_valid:
                reason = f"'{user_id}' is flagged as an invalid / stale account."
            elif has_access:
                reason = f"'{user_id}' has '{access_type}' access to {app_name}."
            else:
                reason = f"'{user_id}' has NO entitlement record for {app_name}."

            results.append(
                EntitlementCheckResult(
                    user_id=user_id,
                    app_name=app_name,
                    has_access=has_access,
                    access_type=access_type,
                    is_valid_user=is_valid,
                    reason=reason,
                )
            )

        return results

    async def execute(self, tool_name: str, **kwargs):
        method = getattr(self, tool_name, None)
        if not method:
            raise ValueError(f"Unknown tool: {tool_name}")
        return await method(**kwargs)
