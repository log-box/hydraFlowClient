import html
import json
import logging
from html import escape
from urllib.parse import urlparse, parse_qs, urlencode

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse, Response, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.schemas import LoginRequestData, ConsentRequestData, LoginSettingsData, ConsentSession

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("hydraApp")
logger.info("Приложение запущено")

app = FastAPI()

# Подключаем статику
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/login_settings", response_model=LoginSettingsData)
async def get_login_settings():
    return LoginSettingsData(
        subject=settings.LOGIN_SUBJECT,
        credential=settings.LOGIN_CREDENTIAL,
        acr=settings.LOGIN_ACR,
        amr=settings.LOGIN_AMR,
        context=settings.LOGIN_CONTEXT,
        extend_session_lifespan=settings.EXTEND_SESSION_LIFESPAN,
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR
    )


@app.get("/favicon.ico")
async def favicon():
    return Response(
        content=b"",  # или отдать реальный .ico файл
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=86400"}
    )


# Отдаём html как корневую страницу
@app.get("/")
async def serve_form():
    return FileResponse("static/auth_form.html")


@app.get("/proxy/clients")
async def proxy_clients():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.HYDRA_PRIVATE_URL}/admin/clients")
        response.raise_for_status()
        return response.json()


@app.get("/logout")
async def serve_logout_page():
    return FileResponse("static/logout.html")


@app.get("/logout_process")
async def logout_endpoint(logout_challenge: str):
    if not isinstance(logout_challenge, str):
        raise HTTPException(status_code=400, detail="logout_challenge must be a string")
    logger.info("Start /logout handler")
    logger.debug(f"Received logout_challenge: {logout_challenge}")

    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/logout/accept"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(url, params={"logout_challenge": logout_challenge})
            response.raise_for_status()
            data = response.json()

            redirect_to = data.get("redirect_to")
            if not redirect_to:
                logger.error("Missing 'redirect_to' in Hydra response")
                raise HTTPException(status_code=500, detail="Hydra response missing 'redirect_to'")

            logger.info(f"Received redirect_to: {redirect_to}")
            return JSONResponse(content={"redirect_to": redirect_to})

    except httpx.HTTPStatusError as e:
        logger.exception("Hydra request failed")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.exception("Unexpected error during logout")
        raise HTTPException(status_code=500, detail=str(e))


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


@app.get("/login")
async def login_endpoint(login_challenge: str):
    await get_client_info_from_challenge(login_challenge)
    login_data = LoginRequestData(
        subject=settings.LOGIN_SUBJECT,
        acr=settings.LOGIN_ACR,
        amr=settings.LOGIN_AMR,
        context=settings.LOGIN_CONTEXT,
        extend_session_lifespan=settings.EXTEND_SESSION_LIFESPAN,
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR,
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login/accept?login_challenge={login_challenge}",
                json=login_data.dict()
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            if not redirect_url:
                raise HTTPException(status_code=500, detail="No redirect URL received from Hydra")
            return RedirectResponse(url=redirect_url, status_code=302)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Login failed")


@app.get("/consent")
async def consent_endpoint(consent_challenge: str):
    print()
    consent_data = ConsentRequestData(
        context=settings.CONSENT_CONTEXT,
        grant_access_token_audience=settings.GRANT_ACCESS_TOKEN_AUDIENCE,
        grant_scope=settings.GRANT_SCOPE,
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR,
        session=ConsentSession(
                id_token=settings.SESSION_ID_TOKEN,
                access_token=settings.SESSION_ACCESS_TOKEN
            )
    )
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent/accept?consent_challenge={consent_challenge}",
                json=consent_data.dict()
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            if not redirect_url:
                raise HTTPException(status_code=500, detail="No redirect URL received from Hydra")
            return RedirectResponse(url=redirect_url, status_code=302)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Consent failed")


@app.get("/redirect-uri")
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


@app.get("/redirect-uri-second")
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
