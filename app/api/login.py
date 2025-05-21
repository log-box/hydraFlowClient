from app.config import settings
from app.schemas import LoginSettingsData, LoginFormSubmitData, ConsentSettingsData, ConsentSession
from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from app.core.hydra import get_client_info_from_challenge
import httpx

router = APIRouter()

@router.get("/login_settings", response_model=LoginSettingsData)
async def get_login_settings():
    return LoginSettingsData(
        subject=settings.LOGIN_SUBJECT,
        credential=settings.LOGIN_CREDENTIAL,
        acr=settings.LOGIN_ACR,
        amr=settings.LOGIN_AMR,
        context=settings.LOGIN_CONTEXT,
        extend_session_lifespan=settings.EXTEND_SESSION_LIFESPAN,
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR,
    )


@router.get("/login")
async def login_form_page():
    return FileResponse("app/static/login.html")  # путь подстрой под себя


@router.post("/login_process")
async def login_endpoint(data: LoginFormSubmitData):
    if not data.continue_:
        return JSONResponse(status_code=501, content={"detail": "В запросе нет данных"})
    await get_client_info_from_challenge(data.login_challenge)
    login_payload = {
        "subject": data.subject,
        "acr": data.acr,
        "amr": data.amr,
        "context": data.context,
        "extend_session_lifespan": data.extend_session_lifespan,
        "remember": data.remember,
        "remember_for": data.remember_for
    }
    settings.LOGIN_CREDENTIAL = data.credential
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login/accept?login_challenge={data.login_challenge}",
                json=login_payload
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            if not redirect_url:
                raise HTTPException(status_code=500, detail="No redirect URL from Hydra")
            return JSONResponse(content={"redirect_url": redirect_url})
            # return RedirectResponse(url=redirect_url, status_code=302)
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra login error")


@router.get("/consent_settings", response_model=ConsentSettingsData)
async def get_consent_settings():
    return ConsentSettingsData(
        grant_access_token_audience=settings.GRANT_ACCESS_TOKEN_AUDIENCE,
        grant_scope=settings.GRANT_SCOPE,
        context=settings.CONSENT_CONTEXT,
        session=ConsentSession(
            id_token=settings.SESSION_ID_TOKEN,
            access_token=settings.SESSION_ACCESS_TOKEN
        ),
        remember=settings.REMEMBER,
        remember_for=settings.REMEMBER_FOR,
    )


