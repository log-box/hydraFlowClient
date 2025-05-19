import os
import json
from dotenv import load_dotenv

load_dotenv()

def str2bool(v: str) -> bool:
    return v.lower() in ("true", "1", "yes")

class Settings:
    def __init__(self):
        missing = [name for name in [
            "HYDRA_PRIVATE_URL", "CLIENT_ID", "REDIRECT_URI", "LOGIN_SUBJECT", "REDIRECT_URI"
        ] if not getattr(self, name)]
        if missing:
            raise RuntimeError(f"Missing required config variables: {', '.join(missing)}")

    HYDRA_PRIVATE_URL = os.getenv("HYDRA_PRIVATE_URL").strip()
    HYDRA_URL = os.getenv("HYDRA_URL").strip()
    HYDRA_OUTSIDE_URL = os.getenv("HYDRA_OUTSIDE_URL").strip()
    CLIENT_ID = os.getenv("CLIENT_ID").strip()
    CLIENT_ID_SECOND = os.getenv("CLIENT_ID_SECOND").strip()
    CLIENT_SECRET = os.getenv("CLIENT_SECRET") # если нужен
    REDIRECT_URI = os.getenv("REDIRECT_URI").strip()
    REDIRECT_URI_SECOND = os.getenv("REDIRECT_URI_SECOND").strip()
    POST_LOGOUT_REDIRECT_URI = os.getenv("POST_LOGOUT_REDIRECT_URI").strip()
    LOGIN_SUBJECT = os.getenv("LOGIN_SUBJECT")
    LOGIN_ACR = os.getenv("LOGIN_ACR")
    LOGIN_AMR = os.getenv("LOGIN_AMR", "").replace("+", " ").split(",")
    LOGIN_CONTEXT = json.loads(os.getenv("LOGIN_CONTEXT", "{}"))
    EXTEND_SESSION_LIFESPAN = str2bool(os.getenv("EXTEND_SESSION_LIFESPAN", "true"))
    REMEMBER = str2bool(os.getenv("REMEMBER", "true"))
    REMEMBER_FOR = int(os.getenv("REMEMBER_FOR", "0"))

    CONSENT_CONTEXT = json.loads(os.getenv("CONSENT_CONTEXT", "{}"))
    GRANT_ACCESS_TOKEN_AUDIENCE = os.getenv("GRANT_ACCESS_TOKEN_AUDIENCE", "").split(",")
    GRANT_SCOPE = os.getenv("GRANT_SCOPE", "").split(",")
    SESSION_ID_TOKEN = json.loads(os.getenv("SESSION_ID_TOKEN", "{}"))
    SESSION_ACCESS_TOKEN = json.loads(os.getenv("SESSION_ACCESS_TOKEN", "{}"))

settings = Settings()
