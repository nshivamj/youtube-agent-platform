from core.session.manager import SessionManager
from core.session.backends.inmemory import InMemoryBackend

# Default singleton — InMemory to start; swap backend without touching anything else.
session_manager = SessionManager(backend=InMemoryBackend())

__all__ = ["SessionManager", "InMemoryBackend", "session_manager"]
