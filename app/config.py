import json
import os
from dotenv import load_dotenv

load_dotenv()


def str2bool(v: str) -> bool:
    return v.lower() in ("true", "1", "yes")


class Settings:
    def __init__(self):
        # Обязательные параметры
        self.HYDRA_PRIVATE_URL = self._required("HYDRA_PRIVATE_URL")
        self.HYDRA_URL = self._required("HYDRA_URL")
        self.HYDRA_OUTSIDE_URL = self._required("HYDRA_OUTSIDE_URL")
        self.CLIENT_ID = self._required("CLIENT_ID")
        self.LOG_LEVEL = self._required("LOG_LEVEL")

        # Опциональные напрямую
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = os.getenv("REDIRECT_URI", "").strip()
        self.POST_LOGOUT_REDIRECT_URI = os.getenv("POST_LOGOUT_REDIRECT_URI", "").strip()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")

        # Настройки по умолчанию
        self.defaults = {
            "ACTIVE_SESSION_INFO": {},
            "ACTIVE_SESSION_ID":"",
            "LOGIN_SUBJECT": "default-d60c-4256-88e2-ac39b7d3e2e6",
            "LOGIN_CREDENTIAL": "DEFAULT",
            "LOGIN_ACR": "DEFAULT",
            "LOGIN_AMR": ["DEFAULT"],
            "EXTEND_SESSION_LIFESPAN": True,
            "REMEMBER": True,
            "REMEMBER_FOR": 0,
            "LOGIN_REQUEST_DATA": {},
            "CONSENT_REQUEST_DATA": {},
            "CONTEXT": {"DEFAULT": "DEFAULT"},
            "GRANT_ACCESS_TOKEN_AUDIENCE": ["MAPIC"],
            "GRANT_SCOPE": ["openid", "offline"],
            "SESSION_ID_TOKEN": {"login": "DEFAULT"},
            "SESSION_ACCESS_TOKEN": {"identity_id": "DEFAULT"}
        }

        for key, default in self.defaults.items():
            raw = os.getenv(key)
            if isinstance(default, bool):
                value = str2bool(raw) if raw is not None else default
            elif isinstance(default, int):
                value = int(raw) if raw is not None else default
            elif isinstance(default, list):
                value = [s.strip() for s in raw.split(",")] if raw else default
            elif isinstance(default, dict):
                value = json.loads(raw) if raw else default
            else:
                value = raw.strip() if raw else default
            setattr(self, key, value)

    @staticmethod
    def _required(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"Missing required config variable: {key}")
        return value.strip()

    def reset_settings(self):

        for key, value in self.defaults.items():
            setattr(self, key, value)


settings = Settings()
