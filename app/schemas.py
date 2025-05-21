from typing import List, Dict, Optional, Any

from pydantic import BaseModel


class ConsentSession(BaseModel):
    id_token: Optional[Dict[str, Any]] = None
    access_token: Optional[Dict[str, Any]] = None


class ConsentSettingsData(BaseModel):
    context: Optional[Dict[str, Any]] = None
    grant_access_token_audience: List[str]
    grant_scope: List[str]
    remember: bool
    remember_for: int
    session: ConsentSession


class ConsentFormSubmitData(ConsentSettingsData):
    consent_challenge: str
    continue_: bool


class LoginSettingsData(BaseModel):
    subject: str
    credential: str
    acr: str
    amr: List[str]
    context: Optional[Dict[str, Any]] = None
    extend_session_lifespan: bool
    remember: bool
    remember_for: int


class LoginFormSubmitData(LoginSettingsData):
    login_challenge: str
    continue_: bool
