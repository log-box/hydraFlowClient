import html
import json
import base64
from typing import Optional
from urllib.parse import urlparse, parse_qs, urlencode

import httpx
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.core.token_payload import validate_jwt_with_jwks
from app.logger import logger

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


def is_valid_payload(p: str | dict) -> str:
    return "ok" if isinstance(p, dict) else "fail"

def decode_payload_unsafe(token: str) -> str:
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return "Неверный формат токена"
        payload_b64 = parts[1] + '=' * (-len(parts[1]) % 4)
        decoded_bytes = base64.urlsafe_b64decode(payload_b64)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Ошибка при декодировании payload: {e}"

async def handle_redirect_uri(request: Request, code: Optional[str], scope: Optional[str], state: Optional[str],
                              error: Optional[str], error_description: Optional[str],
                              client_id: str, redirect_uri: str) -> HTMLResponse:
    logger.info("Start /redirect-uri handler")

    if error:
        html_content = f"""
        <html>
            <head><meta charset="utf-8"><title>Ошибка входа</title></head>
            <body>
                <h2>Ошибка входа</h2>
                <p><strong>{html.escape(error)}</strong>: {html.escape(error_description or '')}</p>
                <a href="/">На главную</a>
            </body>
        </html>
        """
        return HTMLResponse(content=html_content)

    if not code or not scope:
        return HTMLResponse("<h1>Некорректный redirect: отсутствует code или scope</h1>", status_code=422)

    token_request_data = {
        "grant_type": "authorization_code",
        "client_id": client_id.strip(),
        "code": code.strip(),
        "redirect_uri": redirect_uri.strip()
    }
    logger.info("`token_request_data': %s", token_request_data)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.HYDRA_URL}/oauth2/token", data=token_request_data)
            response.raise_for_status()
            token_data = response.json()
            id_token = token_data.get("id_token")
            if not id_token:
                raise HTTPException(status_code=500, detail="Missing id_token in token response")
            params = {
                "id_token_hint": id_token,
                "post_logout_redirect_uri": state,
                "state": state
            }
            logout_uri = f"{settings.HYDRA_OUTSIDE_URL}/oauth2/sessions/logout?{urlencode(params)}"
            id_token_payload = validate_jwt_with_jwks(id_token) if id_token else "access_token отсутствует"
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            access_token_payload = validate_jwt_with_jwks(access_token) if access_token else "access_token отсутствует"
            parsed = urlparse(logout_uri)
            base_logout_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            query_params = parse_qs(parsed.query)
            raw_payloads = []
            for tok in (id_token, access_token):
                if tok:
                    raw_payloads.append(get_raw_payload(tok))
            decoded_payload = "\n\n---\n\n".join(raw_payloads)
            id_token_hint = query_params.get("id_token_hint", [""])[0]
            post_logout_redirect_uri = query_params.get("post_logout_redirect_uri", [""])[0]
            state = query_params.get("state", [""])[0]
            logger.info(f"Сформирован logout_uri: {base_logout_url}")
            post_logout_redirect_uris = settings.LOGIN_REQUEST_DATA.get("client", {}).get("post_logout_redirect_uris",
                                                                                          [])
            return templates.TemplateResponse(
                "redirect_result.html.jinja",
                {
                    "request": request,
                    "token_data": json.dumps(token_data, indent=4),
                    "id_token_payload": json.dumps(id_token_payload, indent=2) if isinstance(id_token_payload,
                                                                                             dict) else id_token_payload,
                    "access_token_payload": json.dumps(access_token_payload, indent=2) if isinstance(
                        access_token_payload, dict) else access_token_payload,
                    "refresh_token": refresh_token,
                    "logout_url": base_logout_url,
                    "id_token_hint": id_token_hint,
                    "post_logout_redirect_uri": post_logout_redirect_uri,  # выбранное
                    "post_logout_redirect_uris": post_logout_redirect_uris,  # список
                    "state": state,
                    "decoded_payload": decoded_payload,
                    "expires_in": token_data.get("expires_in", "—"),
                    "hydra_url": settings.HYDRA_URL,
                    "id_token_validation_status": is_valid_payload(id_token_payload),
                    "access_token_validation_status": is_valid_payload(access_token_payload)
                }
            )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "Token exchange failed",
                "request_data": token_request_data,
                "response_text": e.response.text
            }
        )


@router.get("/redirect-uri")
async def redirect_uri_endpoint(
        request: Request,
        code: Optional[str] = None,
        scope: Optional[str] = None,
        state: Optional[str] = None,
        error: Optional[str] = None,
        error_description: Optional[str] = None
):
    logger.info(f"CLIENT_ID: {settings.CLIENT_ID}")
    return await handle_redirect_uri(
        request, code, scope, state, error, error_description,
        client_id=settings.CLIENT_ID,
        redirect_uri=settings.REDIRECT_URI
    )


@router.get("/redirect-uri-second")
async def redirect_uri_second_endpoint(
        request: Request,
        code: Optional[str] = None,
        scope: Optional[str] = None,
        state: Optional[str] = None,
        error: Optional[str] = None,
        error_description: Optional[str] = None
):
    logger.info(f"CLIENT_ID: {settings.CLIENT_ID}")
    return await handle_redirect_uri(
        request, code, scope, state, error, error_description,
        client_id=settings.CLIENT_ID,
        redirect_uri=settings.REDIRECT_URI
    )




def get_raw_payload(token: str) -> str:
    try:
        payload_part = token.split('.')[1]
        padded = payload_part + '=' * (-len(payload_part) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Ошибка декодирования payload: {str(e)}"