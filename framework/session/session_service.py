"""Session service — workflow-level shared state built on top of the state store.

Provides scoped get/set with session, user, and app scopes.
Acts as the shared blackboard between agents in a workflow.
"""

import logging
from framework.state.state_store import state_store

logger = logging.getLogger("platform.session")


class SessionService:
    def __init__(self, store=None):
        self._store = store or state_store

    def get(self, key: str, scope: str = "session", scope_id: str | None = None, default=None):
        return self._store.get(key, scope=scope, scope_id=scope_id, default=default)

    def set(self, key: str, value, scope: str = "session", scope_id: str | None = None):
        self._store.set(key, value, scope=scope, scope_id=scope_id)

    def get_session_state(self, session_id: str) -> dict:
        keys = self._store.list_keys(scope="session", scope_id=session_id)
        prefix = f"session:{session_id}:"
        return {k.removeprefix(prefix): self._store.get(k.removeprefix(prefix), scope="session", scope_id=session_id) for k in keys}


session_service = SessionService()
