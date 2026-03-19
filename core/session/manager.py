"""
SessionManager — the only session object the framework and runtime touch.

It delegates all storage to whatever AbstractSessionBackend is injected.
Swap the backend (InMemory → Redis → DB) without changing a single line
of framework or runtime code.

Usage
-----
    # bootstrap (once)
    from core.session.backends.inmemory import InMemoryBackend
    from core.session.manager import SessionManager

    session_manager = SessionManager(backend=InMemoryBackend())

    # inside a run
    await session_manager.open(user_id="u1", session_id="s1")

    session_manager.write("analysis_result", {...})
    result = session_manager.read("analysis_result")

    session_manager.close()          # clears state after run
"""
import logging
from typing import Any

from core.session.base import AbstractSessionBackend
from core.session.backends.inmemory import InMemoryBackend

logger = logging.getLogger("platform.session")


class SessionManager:
    """
    Thin, backend-agnostic session manager.

    The runtime calls open() at the start of each run and close() at the
    end.  Agents/callbacks call write() and read() in between.
    """

    def __init__(self, backend: AbstractSessionBackend | None = None, app_name: str = "youtube_platform") -> None:
        self._backend: AbstractSessionBackend = backend or InMemoryBackend()
        self.app_name = app_name
        self._current_session_id: str | None = None

    # ------------------------------------------------------------------
    # Lifecycle — called by Runtime
    # ------------------------------------------------------------------

    async def open(self, user_id: str, session_id: str):
        """
        Start a session.  Returns the ADK Session object so the Runner
        can be initialised.  Everything else in the framework uses
        write() / read() instead of touching the ADK session directly.
        """
        session = await self._backend.get_or_create(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        self._current_session_id = session_id
        logger.debug("Session opened: %s / %s", user_id, session_id)
        return session

    def close(self) -> None:
        """Drop all keys written during this run."""
        if self._current_session_id:
            self._backend.clear(self._current_session_id)
            logger.debug("Session closed: %s", self._current_session_id)
            self._current_session_id = None

    # ------------------------------------------------------------------
    # Key-value output store — called by agents / callbacks
    # ------------------------------------------------------------------

    def write(self, key: str, value: Any) -> None:
        """Write an agent output for the current session."""
        if not self._current_session_id:
            raise RuntimeError("No active session. Call open() first.")
        self._backend.write(self._current_session_id, key, value)

    def read(self, key: str, default: Any = None) -> Any:
        """Read an agent output from the current session."""
        if not self._current_session_id:
            return default
        return self._backend.read(self._current_session_id, key, default)

    def all(self) -> dict[str, Any]:
        """Return all outputs written in the current session."""
        if not self._current_session_id:
            return {}
        return self._backend.all(self._current_session_id)

    # ------------------------------------------------------------------
    # ADK plumbing — used only by Runtime to wire up the Runner
    # ------------------------------------------------------------------

    @property
    def adk_service(self):
        """ADK session service — pass this to google.adk.runners.Runner."""
        return self._backend.adk_service

    @property
    def session_id(self) -> str | None:
        return self._current_session_id
