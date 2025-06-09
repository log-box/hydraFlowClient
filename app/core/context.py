class SessionContext:
    def __init__(self):
        self.ACTIVE_SESSION_INFO = {}
        self.ACTIVE_SESSION_ID = ""
        self.LOGIN_SUBJECT = "default-d60c-4256-88e2-ac39b7d3e2e6"
        self.LOGIN_CREDENTIAL = "DEFAULT"
        self.LOGIN_ACR = "DEFAULT"
        self.LOGIN_AMR = ["DEFAULT"]
        self.EXTEND_SESSION_LIFESPAN = True
        self.REMEMBER = True
        self.REMEMBER_FOR = 0
        self.LOGIN_REQUEST_DATA = {}
        self.CONSENT_REQUEST_DATA = {}
        self.CONTEXT = {"DEFAULT": "DEFAULT"}
        self.GRANT_ACCESS_TOKEN_AUDIENCE = ["MAPIC"]
        self.GRANT_SCOPE = ["openid", "offline"]
        self.SESSION_ID_TOKEN = {"login": "DEFAULT"}
        self.SESSION_ACCESS_TOKEN = {"identity_id": "DEFAULT"}

    def reset(self):
        self.__init__()

    def copy_from(self, other: "SessionContext"):
        for attr, value in other.__dict__.items():
            setattr(self, attr, value)


def load_session_info(context: SessionContext, session_info: dict):
    context.ACTIVE_SESSION_INFO = session_info
    context.LOGIN_CREDENTIAL = session_info.get("session_id_token", {}).get("login", "")
    context.LOGIN_ACR = session_info.get("acr", "").strip()
    context.LOGIN_AMR = session_info.get("amr", [])
    context.CONTEXT = session_info.get("context", {})
    context.GRANT_ACCESS_TOKEN_AUDIENCE = session_info.get("granted_at_audience", [])
    scope = session_info.get("granted_scope", [])
    context.GRANT_SCOPE = scope if isinstance(scope, list) else scope.split(",")

    context.SESSION_ID_TOKEN = session_info.get("session_id_token", {})
    context.SESSION_ACCESS_TOKEN = session_info.get("session_access_token", {})
