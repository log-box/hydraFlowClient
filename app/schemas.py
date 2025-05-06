from pydantic import BaseModel
from typing import List, Dict, Optional

class LoginRequestData(BaseModel):
    subject: str
    acr: str
    amr: List[str]
    context: Optional[Dict]
    extend_session_lifespan: bool
    remember: bool
    remember_for: int

class ConsentRequestData(BaseModel):
    context: Dict
    grant_access_token_audience: List[str]
    grant_scope: List[str]
    remember: bool
    remember_for: int
    session: Dict
