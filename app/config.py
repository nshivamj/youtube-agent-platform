"""Platform configuration — loaded from environment variables / .env file."""

import os

from dotenv import load_dotenv

load_dotenv()


class PlatformConfig:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    MODEL: str = os.getenv("MODEL", "gemini-2.5-flash")
    APP_NAME: str = os.getenv("APP_NAME", "adk_platform")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls) -> None:
        """Raise EnvironmentError if required variables are missing."""
        if not cls.GOOGLE_API_KEY:
            raise EnvironmentError(
                "Missing required environment variable: GOOGLE_API_KEY\n"
                "Copy .env.example to .env and add your key."
            )


config = PlatformConfig()
