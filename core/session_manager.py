from google.adk.sessions import InMemorySessionService
import logging

logger = logging.getLogger("platform.session")


class SessionManager:
    """Manages session state across agent runs.
    Three scopes: session (current convo), user: (persists), app: (global config).
    Session state is the shared blackboard — agents write, other agents read."""

    def __init__(self, app_name: str = "youtube_platform"):
        self.app_name = app_name
        self._service = InMemorySessionService()
        self._current_session = None

    async def get_or_create(self, user_id: str, session_id: str):
        try:
            session = await self._service.get_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
        except Exception:
            session = await self._service.create_session(
                app_name=self.app_name,
                user_id=user_id,
                session_id=session_id
            )
        self._current_session = session
        return session

    def save(self, key: str, value):
        if self._current_session:
            self._current_session.state[key] = value

    def get(self, key: str, default=None):
        if self._current_session:
            return self._current_session.state.get(key, default)
        return default

    def get_state(self) -> dict:
        if self._current_session:
            return dict(self._current_session.state)
        return {}

    @property
    def service(self):
        return self._service


session_manager = SessionManager()
