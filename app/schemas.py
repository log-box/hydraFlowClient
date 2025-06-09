from typing import List, Dict, Optional, Any

from pydantic import BaseModel, Field


class ConsentSession(BaseModel):
    id_token: Optional[Dict[str, Any]] = None
    access_token: Optional[Dict[str, Any]] = None


class ClientData(BaseModel):
    post_logout_redirect_uris: Optional[List[str]] = None


class ConsentSettingsData(BaseModel):
    session_id: str
    context: Any = Field(..., description="Raw JSON object")
    grant_access_token_audience: List[str]
    grant_scope: List[str]
    remember: bool
    remember_for: int
    session: ConsentSession
    active_session_info: Optional[Dict[str, Any]] = None
    client: ClientData


class ConsentFormSubmitData(BaseModel):
    session_id: str = None
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
    session_id: str
    subject: str
    credential: str
    acr: str
    amr: List[str]
    context: Any = Field(..., description="Raw JSON object")
    extend_session_lifespan: bool
    remember: bool
    remember_for: int
    active_session_info: Optional[Dict[str, Any]] = None


class LoginFormSubmitData(BaseModel):
    session_id: str = None
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
