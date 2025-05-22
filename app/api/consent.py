import httpx
from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse, JSONResponse
from app.logger import logger
from app.config import settings
from app.core.hydra import get_consent_info_from_challenge
from app.schemas import ConsentFormSubmitData

router = APIRouter()


@router.get("/consent")
async def login_form_page():
    logger.info("Start /consent handler")
    return FileResponse("app/static/consent.html")  # путь подстрой под себя


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
    await get_consent_info_from_challenge(data.consent_challenge)

    # Преобразуем Pydantic-модель в dict и добавим/переопределим поля
    session_data = {
        "id_token": {
            **(data.session.id_token or {}),
            # "custom_claim": "value",
            "login": settings.LOGIN_CREDENTIAL,
        },
        "access_token": {
            **(data.session.access_token or {}),
            # "identity_id": "111",
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
