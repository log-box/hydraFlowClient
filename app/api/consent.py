import httpx
from fastapi import HTTPException, APIRouter, Query
from fastapi.responses import FileResponse, JSONResponse
from app.logger import logger
from app.config import settings
from app.core.hydra import get_consent_info_from_challenge
from app.schemas import ConsentFormSubmitData, ConsentSettingsData, ConsentSession

router = APIRouter()



@router.get("/consent_settings", response_model=ConsentSettingsData)
async def get_consent_settings(consent_challenge: str = Query(...)):
    logger.info("Start /consent_settings handler")
    await get_consent_info_from_challenge(consent_challenge)
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

@router.get("/consent_request_data")
async def get_consent_request_data():
    logger.info("Start /consent_request_data handler")
    return settings.CONSENT_REQUEST_DATA


@router.get("/consent")
async def consent_form_page():
    logger.info("Start /consent handler")
    return FileResponse("app/static/consent.html")

@router.post("/consent_process")
async def consent_endpoint(data: ConsentFormSubmitData):
    logger.info("Start /consent_process handler")
    if not data.continue_:
        reject_payload = {
            "error": data.error or "access_denied",
            "error_description": data.error_description or "Пользователь отказался от согласия",
        }
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent/reject?consent_challenge={data.consent_challenge}",
                json=reject_payload
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            return JSONResponse(content={"redirect_url": redirect_url})
    # Преобразуем Pydantic-модель в dict и добавим/переопределим поля
    session_data = {
        "id_token": {
            **(data.session.id_token or {}),
            "login": settings.LOGIN_CREDENTIAL,
        },
        "access_token": {
            **(data.session.access_token or {}),
        }
    }

    consent_payload = {
        "context": data.context,
        "grant_access_token_audience": data.grant_access_token_audience,
        "grant_scope": data.grant_scope,
        "session": session_data,
        "remember": data.remember,
        "remember_for": data.remember_for,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/consent/accept?consent_challenge={data.consent_challenge}",
                json=consent_payload
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            if not redirect_url:
                raise HTTPException(status_code=500, detail="No redirect URL received from Hydra")
            return JSONResponse(content={"redirect_url": redirect_url})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra Consent failed")
