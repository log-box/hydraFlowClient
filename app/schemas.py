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


class ConsentFormSubmitData(BaseModel):
    consent_challenge: str
    continue_: bool
    context: Optional[Dict[str, Any]] = None
    grant_access_token_audience: Optional[List[str]] = None
    grant_scope: Optional[List[str]] = None
    remember: Optional[bool] = None
    remember_for: Optional[int] = None
    session: Optional[ConsentSession] = None
    error: Optional[str] = None
    error_description: Optional[str] = None


class LoginSettingsData(BaseModel):
    subject: str
    credential: str
    acr: str
    amr: List[str]
    context: Optional[Dict[str, Any]] = None
    extend_session_lifespan: bool
    remember: bool
    remember_for: int


class LoginFormSubmitData(BaseModel):
    login_challenge: str
    continue_: bool
    subject: Optional[str] = None
    credential: Optional[str] = None
    acr: Optional[str] = None
    amr: Optional[List[str]] = None
    context: Optional[Dict[str, Any]] = None
    extend_session_lifespan: Optional[bool] = None
    remember: Optional[bool] = None
    remember_for: Optional[int] = None
    error: Optional[str] = None
    error_description: Optional[str] = None
