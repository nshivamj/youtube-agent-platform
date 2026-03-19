"""
Abstract session backend.

Implement this to swap InMemory → Redis / DB without touching
SessionManager or anything in framework/.
"""
from abc import ABC, abstractmethod
from typing import Any


class AbstractSessionBackend(ABC):
    """
    Contract every session backend must fulfill.

    Framework and runtime only depend on this interface,
    never on a concrete implementation.
    """

    # ------------------------------------------------------------------
    # ADK integration
    # ------------------------------------------------------------------

    @property
    @abstractmethod
    def adk_service(self):
        """Return the ADK-compatible session service (passed to Runner)."""

    @abstractmethod
    async def get_or_create(self, app_name: str, user_id: str, session_id: str):
        """Return an existing ADK Session or create a new one."""

    # ------------------------------------------------------------------
    # Key-value output store
    # ------------------------------------------------------------------

    @abstractmethod
    def write(self, session_id: str, key: str, value: Any) -> None:
        """Persist an agent output keyed by (session_id, key)."""

    @abstractmethod
    def read(self, session_id: str, key: str, default: Any = None) -> Any:
        """Retrieve an agent output."""

    @abstractmethod
    def all(self, session_id: str) -> dict[str, Any]:
        """Return every key written for this session."""

    @abstractmethod
    def clear(self, session_id: str) -> None:
        """Drop all keys for a session (called after run completes)."""
