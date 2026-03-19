"""In-memory state store with namespace scoping.

Namespace pattern:
  session:{session_id}:{key}
  user:{user_id}:{key}
  app:{key}
"""

import logging

logger = logging.getLogger("platform.state")


class StateStore:
    def __init__(self):
        self._data: dict[str, object] = {}

    def _build_key(self, scope: str, scope_id: str | None, key: str) -> str:
        if scope == "app":
            return f"app:{key}"
        return f"{scope}:{scope_id}:{key}"

    def get(self, key: str, scope: str = "session", scope_id: str | None = None, default=None):
        full_key = self._build_key(scope, scope_id, key)
        return self._data.get(full_key, default)

    def set(self, key: str, value, scope: str = "session", scope_id: str | None = None):
        full_key = self._build_key(scope, scope_id, key)
        self._data[full_key] = value
        logger.debug("state.set %s", full_key)

    def delete(self, key: str, scope: str = "session", scope_id: str | None = None):
        full_key = self._build_key(scope, scope_id, key)
        self._data.pop(full_key, None)

    def list_keys(self, scope: str = "session", scope_id: str | None = None) -> list[str]:
        prefix = f"{scope}:{scope_id}:" if scope != "app" else "app:"
        return [k for k in self._data if k.startswith(prefix)]

    def clear(self):
        self._data.clear()


state_store = StateStore()
