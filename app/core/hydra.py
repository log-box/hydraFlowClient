from urllib.parse import urlparse, parse_qs

import httpx
from fastapi import HTTPException

from app.config import settings
from app.core.context import load_session_info
from app.core.database import fetch_latest_flow_by_session_and_subject
from app.logger import logger


async def get_client_info_from_challenge(login_challenge: str) -> bool:
    logger.info("Fetching login request: %s", login_challenge)
    if not isinstance(login_challenge, str):
        raise HTTPException(status_code=400, detail="login_challenge must be a string")

    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"login_challenge": login_challenge})
            response.raise_for_status()
            login_request_data = response.json()
            logger.info("`login_request_data': %s", login_request_data)
        request_url = login_request_data.get("request_url")
        subject = login_request_data.get("subject")
        logger.info(
            f"subject: {subject}; session_id: {login_request_data.get('session_id')}")
        if subject:
            settings.reset_settings()
            settings.LOGIN_SUBJECT = subject
            settings.LOGIN_REQUEST_DATA = login_request_data
            settings.ACTIVE_SESSION_ID = settings.LOGIN_REQUEST_DATA.get("session_id")
            settings.ACTIVE_SESSION_INFO = fetch_latest_flow_by_session_and_subject(settings.ACTIVE_SESSION_ID, subject)
            logger.info(f"settings.ACTIVE_SESSION_INFO {settings.ACTIVE_SESSION_INFO} ")
            settings.GRANT_ACCESS_TOKEN_AUDIENCE = settings.LOGIN_REQUEST_DATA.get("requested_access_token_audience")
            settings.GRANT_SCOPE = settings.LOGIN_REQUEST_DATA.get("requested_scope")
            if settings.ACTIVE_SESSION_INFO:
                load_session_info(settings.ACTIVE_SESSION_INFO)
        if not request_url:
            logger.error("Hydra response missing 'request_url': %s", request_url)
            raise HTTPException(status_code=500, detail="Hydra response missing 'request_url'")

        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        client_id = query_params.get("client_id", [None])[0]
        redirect_uri = query_params.get("redirect_uri", [None])[0]

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="Missing client_id or redirect_uri in request_url")

        settings.CLIENT_ID = client_id
        settings.LOGIN_REQUEST_DATA = login_request_data
        logger.info(f"LOGIN_REQUEST_DATA: {settings.LOGIN_REQUEST_DATA}")
        settings.REDIRECT_URI = redirect_uri
        return True

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def get_consent_info_from_challenge(consent_challenge: str) -> bool:
    logger.info("Fetching consent request: %s", consent_challenge)
    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"consent_challenge": consent_challenge})
        response.raise_for_status()
        data = response.json()
        settings.CONSENT_REQUEST_DATA = data
        logger.info(f"CONSENT_REQUEST_DATA: {settings.CONSENT_REQUEST_DATA}")
        return True
