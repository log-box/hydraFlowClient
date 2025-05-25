import os
import json
from dotenv import load_dotenv

load_dotenv()

def str2bool(v: str) -> bool:
    return v.lower() in ("true", "1", "yes")

class Settings:
    def __init__(self):
        missing = [name for name in [
            "HYDRA_PRIVATE_URL", "HYDRA_URL", "HYDRA_OUTSIDE_URL"
        ] if not getattr(self, name)]
        if missing:
            raise RuntimeError(f"Missing required config variables: {', '.join(missing)}")

    HYDRA_PRIVATE_URL = os.getenv("HYDRA_PRIVATE_URL").strip()
    HYDRA_URL = os.getenv("HYDRA_URL").strip()
    HYDRA_OUTSIDE_URL = os.getenv("HYDRA_OUTSIDE_URL").strip()
    CLIENT_ID = os.getenv("CLIENT_ID").strip()
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    REDIRECT_URI = os.getenv("REDIRECT_URI").strip()
    POST_LOGOUT_REDIRECT_URI = os.getenv("POST_LOGOUT_REDIRECT_URI").strip()
    LOGIN_SUBJECT = os.getenv("LOGIN_SUBJECT")
    LOGIN_CREDENTIAL = os.getenv("LOGIN_CREDENTIAL")
    LOGIN_ACR = os.getenv("LOGIN_ACR", "").strip()
    LOGIN_AMR = [s.strip() for s in os.getenv("LOGIN_AMR", "").split(",") if s.strip()]
    LOGIN_CONTEXT = json.loads(os.getenv("LOGIN_CONTEXT", "{}"))
    LOGIN_REQUEST_DATA = json.loads(os.getenv("LOGIN_REQUEST_DATA", "{}"))
    CONSENT_REQUEST_DATA = json.loads(os.getenv("CONSENT_REQUEST_DATA", "{}"))
    EXTEND_SESSION_LIFESPAN = str2bool(os.getenv("EXTEND_SESSION_LIFESPAN", "true"))
    REMEMBER = str2bool(os.getenv("REMEMBER", "true"))
    REMEMBER_FOR = int(os.getenv("REMEMBER_FOR", "0"))

    CONSENT_CONTEXT = json.loads(os.getenv("CONSENT_CONTEXT", "{}"))
    GRANT_ACCESS_TOKEN_AUDIENCE = [s.strip() for s in os.getenv("GRANT_ACCESS_TOKEN_AUDIENCE", "").split(",") if
                                   s.strip()]
    GRANT_SCOPE = os.getenv("GRANT_SCOPE", "").split(",")
    SESSION_ID_TOKEN = json.loads(os.getenv("SESSION_ID_TOKEN", "{}"))
    SESSION_ACCESS_TOKEN = json.loads(os.getenv("SESSION_ACCESS_TOKEN", "{}"))
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = int(os.getenv("DB_PORT", "5432"))
    DB_NAME = os.getenv("DB_NAME")
    DB_USER = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")

settings = Settings()
