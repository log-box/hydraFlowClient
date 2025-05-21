import httpx
from fastapi import HTTPException
from urllib.parse import urlparse, parse_qs
from app.config import settings


async def get_client_info_from_challenge(login_challenge: str) -> bool:
    if not isinstance(login_challenge, str):
        raise HTTPException(status_code=400, detail="login_challenge must be a string")

    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"login_challenge": login_challenge})
            response.raise_for_status()
            data = response.json()

        request_url = data.get("request_url")
        if not request_url:
            raise HTTPException(status_code=500, detail="Hydra response missing 'request_url'")

        parsed = urlparse(request_url)
        query_params = parse_qs(parsed.query)

        client_id = query_params.get("client_id", [None])[0]
        redirect_uri = query_params.get("redirect_uri", [None])[0]

        if not client_id or not redirect_uri:
            raise HTTPException(status_code=500, detail="Missing client_id or redirect_uri in request_url")

        settings.CLIENT_ID = client_id
        settings.REDIRECT_URI = redirect_uri
        settings.REDIRECT_URI_SECOND = redirect_uri
        return True

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra request failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def get_consent_info_from_challenge(consent_challenge: str) -> dict:
    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent"
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params={"consent_challenge": consent_challenge})
        response.raise_for_status()
        return response.json()
