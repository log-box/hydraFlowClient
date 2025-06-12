import base64
import html
import json
from typing import Optional
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.core.context import SessionContext
from app.core.context_storage import get_session_context, get_session_id_by_state
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


def get_raw_payload(token: str) -> str:
    try:
        payload_part = token.split('.')[1]
        padded = payload_part + '=' * (-len(payload_part) % 4)
        decoded_bytes = base64.urlsafe_b64decode(padded)
        return decoded_bytes.decode('utf-8')
    except Exception as e:
        return f"Ошибка декодирования payload: {str(e)}"


async def handle_redirect_uri(
        request: Request,
        code: Optional[str],
        scope: Optional[str],
        state: Optional[str],
        error: Optional[str],
        error_description: Optional[str],
        client_id: str,
        redirect_uri: str,
        context: SessionContext
) -> HTMLResponse:
    logger.info("Start /redirect-uri handler")

    if error:
        html_content = f"""
        <html>
          <head>
            <meta charset="utf-8">
            <title>Ошибка входа</title>
            <style>
              html, body {{
                margin: 0;
                padding: 0;
                font-family: "Segoe UI", Roboto, sans-serif;
                background: linear-gradient(145deg, #f0f4f8, #ffffff);
                color: #2c3e50;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
              }}
              .container {{
                background: white;
                border: 1px solid #e0e6ed;
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.05);
                max-width: 480px;
                width: 90%;
                text-align: center;
              }}
              h2 {{
                font-size: 1.5rem;
                margin-bottom: 1rem;
              }}
              p {{
                font-size: 1rem;
                color: #333;
                margin-bottom: 1.5rem;
              }}
              .error-code {{
                font-weight: bold;
                color: #dc3545;
              }}
              a {{
                display: inline-block;
                margin-top: 1rem;
                padding: 0.6rem 1.2rem;
                background-color: #007bff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                font-size: 0.95rem;
              }}
              a:hover {{
                background-color: #0056b3;
              }}
            </style>
          </head>
          <body>
            <div class="container">
              <h2>Ошибка входа</h2>
              <p><span class="error-code">{html.escape(error)}</span>: {html.escape(error_description or '')}</p>
              <a href="/">На главную</a>
            </div>
          </body>
        </html>
        """

        return HTMLResponse(content=html_content)

    if not code or not scope:
        html_content = """
        <html>
          <head>
            <meta charset="utf-8">
            <title>Ошибка 422 — Некорректный redirect</title>
            <style>
              html, body {
                margin: 0;
                padding: 0;
                font-family: "Segoe UI", Roboto, sans-serif;
                background: #fff5f5;
                color: #2c3e50;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
              }
              .container {
                background: white;
                border: 1px solid #f5c6cb;
                border-radius: 12px;
                padding: 2rem;
                box-shadow: 0 0 10px rgba(220, 53, 69, 0.1);
                max-width: 480px;
                width: 90%;
                text-align: center;
              }
              h1 {
                color: #dc3545;
                font-size: 1.3rem;
                margin-bottom: 1rem;
              }
              p {
                color: #555;
                font-size: 0.95rem;
              }
            </style>
          </head>
          <body>
            <div class="container">
              <h1>Некорректный redirect</h1>
              <p>Отсутствует параметр <code>code</code> или <code>scope</code> в URL.</p>
            </div>
          </body>
        </html>
        """
        return HTMLResponse(content=html_content, status_code=422)

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

            id_token_payload = validate_jwt_with_jwks(id_token)
            access_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            access_token_payload = validate_jwt_with_jwks(access_token) if access_token else "access_token отсутствует"

            raw_payloads = [get_raw_payload(tok) for tok in (id_token, access_token) if tok]
            decoded_payload = "\n\n---\n\n".join(raw_payloads)

            post_logout_redirect_uris = context.LOGIN_REQUEST_DATA.get("client", {}).get("post_logout_redirect_uris",
                                                                                         [])
            logger.info(f"Сформирован logout_uri: {logout_uri}")
            logger.info(f"Сформирован LOGIN_REQUEST_DATA: {context.LOGIN_REQUEST_DATA}")
            logger.info(f"Сформирован post_logout_redirect_uris: {post_logout_redirect_uris}")

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
                    "logout_url": logout_uri,
                    "id_token_hint": id_token,
                    "post_logout_redirect_uri": state,
                    "post_logout_redirect_uris": post_logout_redirect_uris,
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
        error_description: Optional[str] = None,
):
    if not state:
        raise HTTPException(status_code=400, detail="Missing state param")

    session_id = get_session_id_by_state(state)
    if not session_id:
        raise HTTPException(status_code=404, detail="Session not found for provided state")

    context = get_session_context(session_id)

    return await handle_redirect_uri(
        request, code, scope, state, error, error_description,
        client_id=settings.CLIENT_ID,
        redirect_uri=settings.REDIRECT_URI,
        context=context
    )


@router.get("/redirect-uri-second")
async def redirect_uri_second_endpoint(
        request: Request,
        code: Optional[str] = None,
        scope: Optional[str] = None,
        state: Optional[str] = None,
        error: Optional[str] = None,
        error_description: Optional[str] = None,
):
    if not state:
        raise HTTPException(status_code=400, detail="Missing state param")

    session_id = get_session_id_by_state(state)
    if not session_id:
        raise HTTPException(status_code=404, detail="Session not found for provided state")

    context = get_session_context(session_id)

    return await handle_redirect_uri(
        request, code, scope, state, error, error_description,
        client_id=settings.CLIENT_ID,
        redirect_uri=settings.REDIRECT_URI,
        context=context
    )
