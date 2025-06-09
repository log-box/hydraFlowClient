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
        self.LOG_PATH = self._required("LOG_PATH")

        # Опциональные параметры
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.REDIRECT_URI = os.getenv("REDIRECT_URI", "").strip()
        self.POST_LOGOUT_REDIRECT_URI = os.getenv("POST_LOGOUT_REDIRECT_URI", "").strip()
        self.DB_HOST = os.getenv("DB_HOST")
        self.DB_PORT = int(os.getenv("DB_PORT", "5432"))
        self.DB_NAME = os.getenv("DB_NAME")
        self.DB_USER = os.getenv("DB_USER")
        self.DB_PASSWORD = os.getenv("DB_PASSWORD")

    @staticmethod
    def _required(key: str) -> str:
        value = os.getenv(key)
        if not value:
            raise RuntimeError(f"Missing required config variable: {key}")
        return value.strip()


settings = Settings()
