"""
InMemory session backend — default / development backend.

Wraps ADK's InMemorySessionService and keeps a plain dict as the
key-value output store.  To switch to Redis or a DB later, create a new
backend module that implements AbstractSessionBackend and inject it into
SessionManager — nothing else changes.
"""
from typing import Any

from google.adk.sessions import InMemorySessionService

from core.session.base import AbstractSessionBackend


class InMemoryBackend(AbstractSessionBackend):

    def __init__(self) -> None:
        self._adk_service = InMemorySessionService()
        # { session_id: { key: value } }
        self._store: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # ADK integration
    # ------------------------------------------------------------------

    @property
    def adk_service(self):
        return self._adk_service

    async def get_or_create(self, app_name: str, user_id: str, session_id: str):
        try:
            session = await self._adk_service.get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
            )
            if session:
                return session
        except Exception:
            pass
        return await self._adk_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id,
        )

    # ------------------------------------------------------------------
    # Key-value output store
    # ------------------------------------------------------------------

    def write(self, session_id: str, key: str, value: Any) -> None:
        self._store.setdefault(session_id, {})[key] = value

    def read(self, session_id: str, key: str, default: Any = None) -> Any:
        return self._store.get(session_id, {}).get(key, default)

    def all(self, session_id: str) -> dict[str, Any]:
        return dict(self._store.get(session_id, {}))

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
