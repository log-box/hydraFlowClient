import httpx
from fastapi import HTTPException, APIRouter, Query
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.core.context import SessionContext
from app.core.context_storage import get_session_context
from app.core.hydra import get_client_info_from_challenge
from app.logger import logger
from app.schemas import LoginSettingsData, LoginFormSubmitData

router = APIRouter()


@router.get("/login_settings", response_model=LoginSettingsData)
async def get_login_settings(login_challenge: str = Query(...)):
    logger.info("Start /login_settings handler")
    context = SessionContext()
    await get_client_info_from_challenge(login_challenge, context=context)
    return LoginSettingsData(
        session_id=context.ACTIVE_SESSION_ID,
        subject=context.LOGIN_SUBJECT,
        credential=context.LOGIN_CREDENTIAL,
        acr=context.LOGIN_ACR,
        amr=context.LOGIN_AMR,
        context=context.CONTEXT,
        extend_session_lifespan=context.EXTEND_SESSION_LIFESPAN,
        remember=context.REMEMBER,
        remember_for=context.REMEMBER_FOR,
        active_session_info=context.ACTIVE_SESSION_INFO or None
    )


@router.get("/login_request_data")
async def get_login_request_data(session_id: str = Query(...)):
    logger.info("Start /login_request_data handler")
    context = get_session_context(session_id)
    return context.LOGIN_REQUEST_DATA


@router.get("/login")
async def login_form_page():
    logger.info("Start /login handler")
    return FileResponse("app/static/login.html")


@router.post("/login_process")
async def login_process(data: LoginFormSubmitData):
    logger.info("Start /login_process handler")
    context = get_session_context(data.session_id)
    if not data.continue_:
        response = await httpx.AsyncClient().put(
            f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login/reject?login_challenge={data.login_challenge}",
            json={
                "error": data.error or "access_denied",
                "error_description": data.error_description or "Пользователь отменил вход",
            }
        )
        logger.info(f"Redirect error: {data.error}, description: {data.error_description}")
        return {"redirect_url": response.json()["redirect_to"]}

    missing = []
    for field in ["subject", "credential", "acr", "amr", "extend_session_lifespan", "remember"]:
        if getattr(data, field) is None:
            missing.append(field)
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing required fields: {', '.join(missing)}")

    login_payload = {
        "subject": data.subject,
        "acr": data.acr,
        "amr": data.amr,
        "context": data.context,
        "extend_session_lifespan": data.extend_session_lifespan,
        "remember": data.remember,
        "remember_for": data.remember_for
    }
    context.LOGIN_CREDENTIAL = data.credential
    logger.info(f"login_payload: {login_payload}")
    logger.info(f"data: {data}")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.put(
                f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/login/accept?login_challenge={data.login_challenge}",
                json=login_payload
            )
            response.raise_for_status()
            redirect_url = response.json().get("redirect_to")
            logger.info(f"login/accept=response: {response}")
            logger.info(f"redirect_url: {redirect_url}")
            if not redirect_url:
                raise HTTPException(status_code=500, detail="No redirect URL from Hydra")
            return JSONResponse(content={"redirect_url": redirect_url})
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail="Hydra login error")
