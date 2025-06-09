from urllib.parse import urlparse, parse_qs

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.context import load_session_info, SessionContext
from app.core.context_storage import set_context, get_context, map_state_to_session
from app.core.database import fetch_latest_flow_by_session_and_subject
from app.logger import logger


async def get_client_info_from_challenge(login_challenge: str, context: SessionContext) -> bool:
    logger.debug(f"Start 'get_client_info_from_challenge' with - login_challenge: {login_challenge}")
    if not isinstance(login_challenge, str):
        raise HTTPException(status_code=400, detail="login_challenge must be a string")

    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"login_challenge": login_challenge})
            response.raise_for_status()
            login_request_data = response.json()

        logger.debug(f"login_request_data: {login_request_data}")
        session_id = login_request_data.get("session_id")
        existing_context = get_context(session_id)
        if existing_context:
            context.copy_from(existing_context)
        request_url = login_request_data.get("request_url")
        subject = login_request_data.get("subject")
        context.ACTIVE_SESSION_INFO = fetch_latest_flow_by_session_and_subject(session_id, subject)
        if context.ACTIVE_SESSION_INFO:
            load_session_info(context, context.ACTIVE_SESSION_INFO)
        if subject:
            context.LOGIN_SUBJECT = subject
        context.LOGIN_REQUEST_DATA = login_request_data
        context.ACTIVE_SESSION_ID = session_id
        context.GRANT_ACCESS_TOKEN_AUDIENCE = login_request_data.get("requested_access_token_audience")
        context.GRANT_SCOPE = login_request_data.get("requested_scope")

        if not request_url:
            logger.error("Hydra response missing 'request_url'")
            raise HTTPException(status_code=500, detail="Hydra response missing 'request_url'")

        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        settings.CLIENT_ID = query_params.get("client_id", [None])[0]
        settings.REDIRECT_URI = query_params.get("redirect_uri", [None])[0]
        state = query_params.get("state", [None])[0]

        if not settings.CLIENT_ID or not settings.REDIRECT_URI:
            raise HTTPException(status_code=500, detail="Missing client_id or redirect_uri in request_url")

        set_context(session_id, context)
        map_state_to_session(state, context.ACTIVE_SESSION_ID)
        return True

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def get_consent_info_from_challenge(consent_challenge: str, context: SessionContext) -> bool:
    logger.info("Fetching consent request: %s", consent_challenge)
    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"consent_challenge": consent_challenge})
            response.raise_for_status()
            data = response.json()

        context.CONSENT_REQUEST_DATA = data
        return True

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra consent request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
