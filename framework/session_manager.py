from enum import Enum
from typing import Any


class SessionScope(str, Enum):
    SESSION = "session"
    USER = "user"
    APP = "app"


class SessionManager:
    def __init__(self):
        self._state: dict[str, Any] = {}

    @staticmethod
    def _key(scope: SessionScope, key: str) -> str:
        return f"{scope.value}:{key}"

    def set(self, scope: SessionScope, key: str, value: Any):
        self._state[self._key(scope, key)] = value

    def get(self, scope: SessionScope, key: str, default: Any = None) -> Any:
        return self._state.get(self._key(scope, key), default)

    def clear(self, scope: SessionScope):
        prefix = f"{scope.value}:"
        keys_to_remove = [k for k in self._state if k.startswith(prefix)]
        for k in keys_to_remove:
            del self._state[k]

    def to_adk_state(self) -> dict:
        return dict(self._state)

    def from_adk_state(self, state: dict):
        self._state.clear()
        for k, v in state.items():
            if any(k.startswith(f"{s.value}:") for s in SessionScope):
                self._state[k] = v


session_manager = SessionManager()
