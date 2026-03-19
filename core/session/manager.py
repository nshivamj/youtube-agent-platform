"""
SessionManager — lifecycle and ADK plumbing only.

State is stored and read via ADK's native session.state (ToolContext.state /
CallbackContext.state). SessionManager's job is to open/close sessions and
expose adk_service so the Runner can be wired up correctly.

Usage
-----
    from core.session.backends.inmemory import InMemoryBackend
    from core.session.manager import SessionManager

    session_manager = SessionManager(backend=InMemoryBackend())

    # inside a run
    await session_manager.open(user_id="u1", session_id="s1")
    # ... agents run, state flows via ToolContext.state ...
    session_manager.close()
"""
import logging

from core.session.base import AbstractSessionBackend
from core.session.backends.inmemory import InMemoryBackend

logger = logging.getLogger("platform.session")


class SessionManager:
    """
    Thin, backend-agnostic session manager.

    The runtime calls open() at the start of each run and close() at the end.
    All state reads/writes during a run go through ADK's ToolContext.state
    and CallbackContext.state — not through this class.
    """

    def __init__(self, backend: AbstractSessionBackend | None = None, app_name: str = "youtube_platform") -> None:
        self._backend: AbstractSessionBackend = backend or InMemoryBackend()
        self.app_name = app_name
        self._current_session_id: str | None = None

    async def open(self, user_id: str, session_id: str):
        """Start a session. Returns the ADK Session so the Runner can be initialised."""
        session = await self._backend.get_or_create(
            app_name=self.app_name,
            user_id=user_id,
            session_id=session_id,
        )
        self._current_session_id = session_id
        logger.debug("Session opened: %s / %s", user_id, session_id)
        return session

    def close(self) -> None:
        """Clear session state after a run."""
        if self._current_session_id:
            self._backend.clear(self._current_session_id)
            logger.debug("Session closed: %s", self._current_session_id)
            self._current_session_id = None

    @property
    def adk_service(self):
        """ADK session service — pass this to google.adk.runners.Runner."""
        return self._backend.adk_service

    @property
    def session_id(self) -> str | None:
        return self._current_session_id
