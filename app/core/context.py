from app.config import settings


def load_session_info(session_info: dict):
    settings.ACTIVE_SESSION_INFO = session_info
    settings.LOGIN_CREDENTIAL = session_info.get("session_id_token", {}).get("login", "")
    settings.LOGIN_ACR = session_info.get("acr", "").strip()
    settings.LOGIN_AMR = session_info.get("amr", [])
    settings.CONTEXT = session_info.get("context", {})
    settings.GRANT_ACCESS_TOKEN_AUDIENCE = session_info.get("granted_at_audience", [])
    scope = session_info.get("granted_scope", [])
    settings.GRANT_SCOPE = scope if isinstance(scope, list) else scope.split(",")

    settings.SESSION_ID_TOKEN = session_info.get("session_id_token", {})
    settings.SESSION_ACCESS_TOKEN = session_info.get("session_access_token", {})
    # return True

