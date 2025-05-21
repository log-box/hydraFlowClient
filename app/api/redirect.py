import html
import json
import logging
from html import escape
from urllib.parse import urlparse, parse_qs, urlencode

import httpx
from fastapi import HTTPException, APIRouter
from fastapi.responses import HTMLResponse

from app.config import settings

router = APIRouter()

logger = logging.getLogger("hydraApp")


@router.get("/redirect-uri")
async def redirect_uri_endpoint(code: str, scope: str, state: str):
    token_request_data = {
        "grant_type": "authorization_code",
        "client_id": settings.CLIENT_ID.strip(),
        "code": code.strip(),
        "redirect_uri": settings.REDIRECT_URI.strip()
    }

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

            pretty_json = html.escape(json.dumps(token_data, indent=4))
            parsed = urlparse(logout_uri)
            base_logout_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
            query_params = parse_qs(parsed.query)

            # Подставляем параметры
            id_token_hint = query_params.get("id_token_hint", [""])[0]
            post_logout_redirect_uri = query_params.get("post_logout_redirect_uri", [""])[0]
            state = query_params.get("state", [""])[0]
            logger.info(f"Сформирован logout_uri: {base_logout_url}")
            html_content = f"""
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Token Info</title>
                    <style>
                        body {{ font-family: sans-serif; }}
                        pre {{
                            white-space: pre-wrap;
                            word-wrap: break-word;
                            background: #f0f0f0;
                            padding: 1em;
                            border-radius: 5px;
                        }}
                        button {{
                            margin-top: 20px;
                            padding: 0.5em 1em;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Ответ от Hydra</h2>
                    <pre>{pretty_json}</pre>

                <form action="{base_logout_url}" method="get">
                    <input type="hidden" name="id_token_hint" value="{escape(id_token_hint)}">
                    <input type="hidden" name="post_logout_redirect_uri" value="{escape(post_logout_redirect_uri)}">
                    <input type="hidden" name="state" value="{escape(state)}">
                    <button type="submit">Выйти!</button>
                </form>
                </body>
            </html>
            """
            logger.info(f"Сформирован html_content: {html_content}")
            return HTMLResponse(content=html_content)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "Token exchange failed",
                "request_data": token_request_data,
                "response_text": e.response.text
            }
        )


@router.get("/redirect-uri-second")
async def redirect_uri_second_endpoint(code: str, scope: str, state: str):
    token_request_data = {
        "grant_type": "authorization_code",
        "client_id": settings.CLIENT_ID_SECOND.strip(),
        "code": code.strip(),
        "redirect_uri": settings.REDIRECT_URI_SECOND.strip()
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.HYDRA_URL}/oauth2/token", data=token_request_data)
            response.raise_for_status()
            token_data = response.json()
            pretty_json = html.escape(json.dumps(token_data, indent=4))
            html_content = f"""
            <html>
                <head>
                    <meta charset="utf-8">
                    <title>Token Info</title>
                    <style>
                        body {{ font-family: sans-serif; }}
                        pre {{
                            white-space: pre-wrap;
                            word-wrap: break-word;
                            background: #f0f0f0;
                            padding: 1em;
                            border-radius: 5px;
                        }}
                        button {{
                            margin-top: 20px;
                            padding: 0.5em 1em;
                        }}
                    </style>
                </head>
                <body>
                    <h2>Ответ от Hydra</h2>
                    <pre>{pretty_json}</pre>

                    <form action="{state}" method="get">
                        <button type="submit">Перейти по state: {state}</button>
                    </form>
                </body>
            </html>
            """
            return HTMLResponse(content=html_content)
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail={
                "error": "Token exchange failed",
                "request_data": token_request_data,
                "response_text": e.response.text
            }
        )
