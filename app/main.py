from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import httpx
from app.config import settings
from app.schemas import LoginRequestData, ConsentRequestData
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI()

# Подключаем статику
app.mount("/static", StaticFiles(directory="static"), name="static")

# Отдаём html как корневую страницу
@app.get("/")
async def serve_form():
    return FileResponse("static/auth_form.html")

@app.get("/proxy/clients")
async def proxy_clients():
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:4445/admin/clients")
        response.raise_for_status()
        return response.json()


@app.get("/login")
async def login_endpoint(login_challenge: str):
    login_data = LoginRequestData(
        subject=settings.LOGIN_SUBJECT,
        acr=settings.LOGIN_ACR,
        amr=settings.LOGIN_AMR,
        context=settings.LOGIN_CONTEXT,
        extend_session_lifespan=settings.EXTEND_SESSION_LIFESPAN,
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR
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
        session={
            "id_token": settings.SESSION_ID_TOKEN,
            "access_token": settings.SESSION_ACCESS_TOKEN
        }
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
    print("token_request_data:", settings.REDIRECT_URI)
    token_request_data = {
        "grant_type": "authorization_code",
        "client_id": settings.CLIENT_ID.strip(),
        "code": code.strip(),
        "redirect_uri": settings.REDIRECT_URI.strip()
    }
    print("token_request_data:", token_request_data)
    print("URL:", f"{settings.HYDRA_URL}/oauth2/token")
    print("CLIENT_ID:", settings.CLIENT_ID)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.HYDRA_URL}/oauth2/token", data=token_request_data)
            response.raise_for_status()
            token_data = response.json()
            return token_data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Token exchange failed")

@app.get("/redirect-uri-second")
async def redirect_uri_second_endpoint(code: str, scope: str, state: str):
    print("token_request_data:", settings.REDIRECT_URI_SECOND)
    token_request_data = {
        "grant_type": "authorization_code",
        "client_id": settings.CLIENT_ID_SECOND.strip(),
        "code": code.strip(),
        "redirect_uri": settings.REDIRECT_URI_SECOND.strip()
    }
    print("token_request_data:", token_request_data)
    print("URL:", f"{settings.HYDRA_URL}/oauth2/token")
    print("CLIENT_ID:", settings.CLIENT_ID_SECOND)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{settings.HYDRA_URL}/oauth2/token", data=token_request_data)
            response.raise_for_status()
            token_data = response.json()
            return token_data
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Token exchange failed")