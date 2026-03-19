"""Entitlement tools — plain functions, registered as ADK FunctionTools on import.

In production, replace _ENTITLEMENT_DB with a real IAM / LDAP / SailPoint call.
"""
from framework.tools.registry import tool

_ENTITLEMENT_DB: dict[str, dict[str, str]] = {
    "salesforce": {"alice": "write", "bob": "read", "carol": "admin", "svc_batch": "read"},
    "jira":       {"alice": "write", "dave": "write", "eve": "read"},
    "confluence": {"alice": "read",  "bob": "write",  "carol": "read", "frank": "admin"},
}

_INVALID_USERS = {"svc_batch", "ghost_user", "former_emp_john"}


@tool()
def check_user_entitlements(app_name: str, users: list) -> list:
    """Check whether users have access to an application.

    Args:
        app_name: Application name to check (e.g. 'Salesforce', 'Jira').
        users: List of user IDs / usernames to validate.

    Returns:
        List of {user_id, app_name, has_access, access_type, is_valid_user, reason}
        — one entry per user.
    """
    app_key = app_name.lower()
    db = _ENTITLEMENT_DB.get(app_key, {})
    results = []
    for user_id in users:
        user_key = user_id.strip().lower()
        is_valid = user_key not in _INVALID_USERS
        access_type = db.get(user_key)
        has_access = access_type is not None
        if not is_valid:
            reason = f"'{user_id}' is flagged as an invalid / stale account."
        elif has_access:
            reason = f"'{user_id}' has '{access_type}' access to {app_name}."
        else:
            reason = f"'{user_id}' has NO entitlement record for {app_name}."
        results.append({
            "user_id": user_id,
            "app_name": app_name,
            "has_access": has_access,
            "access_type": access_type,
            "is_valid_user": is_valid,
            "reason": reason,
        })
    return results
