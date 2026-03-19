import os
from typing import Any


class SessionManager:
    """Scoped key-value store. Key format: '{scope}:{key}'."""

    def __init__(self):
        self._session: dict[str, Any] = {}   # per-run, wiped after each run
        self._user: dict[str, dict[str, Any]] = {}  # keyed by user_id
        self._app: dict[str, Any] = {}        # populated once at startup

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get(self, scope_key: str, default: Any = None) -> Any:
        scope, key = self._parse(scope_key)
        if scope == "session":
            return self._session.get(key, default)
        if scope == "app":
            return self._app.get(key, default)
        # user scope — return None if user bucket doesn't exist
        return self._user.get("_current", {}).get(key, default)

    def set(self, scope_key: str, value: Any) -> None:
        scope, key = self._parse(scope_key)
        if scope == "session":
            self._session[key] = value
        elif scope == "app":
            self._app[key] = value
        else:
            bucket = self._user.setdefault("_current", {})
            bucket[key] = value

    def get_or_create(self, user_id: str, session_id: str) -> dict:
        if user_id not in self._user:
            self._user[user_id] = {}
        self._user["_current"] = self._user[user_id]
        return self._user[user_id]

    def clear_session_scope(self) -> None:
        self._session.clear()

    def init_app_scope(self) -> None:
        self._app["tool_mode"] = os.getenv("TOOL_MODE", "local")
        raw = os.getenv("ALLOWED_AGENTS", "*")
        self._app["allowed_agents"] = raw
        self._app["auto_approve"] = os.getenv("AUTO_APPROVE", "false").lower()

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    @staticmethod
    def _parse(scope_key: str) -> tuple[str, str]:
        if ":" not in scope_key:
            raise ValueError(f"Invalid scope_key '{scope_key}'. Expected 'scope:key'.")
        scope, key = scope_key.split(":", 1)
        if scope not in ("session", "user", "app"):
            raise ValueError(f"Unknown scope '{scope}'. Must be session, user, or app.")
        return scope, key


# Module-level singleton
session_mgr = SessionManager()
