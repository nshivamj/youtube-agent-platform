"""
Entitlement checking tool.

In production this would call your IAM / LDAP / SailPoint API.
Here we provide a realistic mock so the agent can run end-to-end without
external dependencies.  Replace _ENTITLEMENT_DB and the network call inside
check_user_entitlements() when you wire up the real API.
"""
from control_testing.schemas import EntitlementCheckResult

# ---------------------------------------------------------------------------
# Mock entitlement database
# Key  : app_name (lower-cased)
# Value: dict mapping user_id → access_type  ("read" | "write" | "admin")
#        Users NOT in the dict have no access.
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

# Users that exist in the system but are flagged as invalid / stale
_INVALID_USERS = {"svc_batch", "ghost_user", "former_emp_john"}


def check_user_entitlements(
    app_name: str,
    users: list[str],
) -> list[EntitlementCheckResult]:
    """
    Check whether a list of users have access to the given application.

    Args:
        app_name: Name of the application to check (e.g. "Salesforce").
        users:    List of user IDs / usernames to validate.

    Returns:
        A list of EntitlementCheckResult — one entry per user — containing
        whether they have access, the access type, and whether they are a
        recognised valid user.
    """
    app_key = app_name.lower()
    app_entitlements: dict[str, str] = _ENTITLEMENT_DB.get(app_key, {})

    results: list[EntitlementCheckResult] = []
    for user_id in users:
        user_key = user_id.strip().lower()
        is_valid = user_key not in _INVALID_USERS
        access_type = app_entitlements.get(user_key)
        has_access = access_type is not None

        reason: str
        if not is_valid:
            reason = f"User '{user_id}' is flagged as an invalid / stale account."
        elif has_access:
            reason = (
                f"User '{user_id}' has '{access_type}' access to {app_name}."
            )
        else:
            reason = (
                f"User '{user_id}' has NO entitlement record for {app_name}."
            )

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
