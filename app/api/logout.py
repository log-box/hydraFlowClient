import httpx
from fastapi import HTTPException, APIRouter, Request
from fastapi.responses import FileResponse, JSONResponse
import jwt
from jwt import InvalidTokenError
from app.config import settings
from app.logger import logger
from app.schemas import LogoutPayload

router = APIRouter()


@router.get("/logout")
async def serve_logout_page():
    logger.info("Start /logout handler")
    return FileResponse("app/static/logout.html")


@router.get("/logout_request_data")
async def get_login_request_data(logout_challenge: str):
    logger.info("Start /logout_request_data handler")
    if not isinstance(logout_challenge, str):
        raise HTTPException(status_code=400, detail="logout_challenge must be a string")
    logger.debug(f"Received logout_challenge: {logout_challenge}")

    url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/logout"

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params={"logout_challenge": logout_challenge})
            response.raise_for_status()
            logout_request_data = response.json()
            if not logout_request_data:
                logger.error("Missing 'logout_request_data' in Hydra response")
                raise HTTPException(status_code=500, detail="Hydra response missing 'logout_request_data'")

            logger.info(f"Received logout_request_data: {logout_request_data}")
            return JSONResponse(content={"logout_request_data": logout_request_data})

    except httpx.HTTPStatusError as e:
        logger.exception("Hydra request failed")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.exception("Unexpected error during logout")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/logout_process")
async def logout_endpoint(request: Request, logout_challenge: str):
    logger.info("Start /logout_process handler")

    if not isinstance(logout_challenge, str):
        raise HTTPException(status_code=400, detail="logout_challenge must be a string")

    # Попытка получить тело запроса
    try:
        body: LogoutPayload = await request.json()
        subject = body.get("subject")
        client_id = body.get("client_id")
    except Exception:
        logger.info("Нет JSON тела или не удалось разобрать. Продолжаем без удаления токенов.")
        subject = None
        client_id = None

    try:
        async with httpx.AsyncClient() as client:
            # Если есть subject — вызываем удаление сессии
            if subject:
                delete_url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/sessions/consent"
                params = {"subject": subject}

                if client_id:
                    params["client"] = client_id
                else:
                    params["all"] = "true"  # <- новый параметр

                logger.info(f"Отзываем токены: {params}")
                delete_resp = await client.delete(delete_url, params=params)
                delete_resp.raise_for_status()
                logger.info("Токены отозваны.")

            # Завершаем logout-челлендж
            accept_url = f"{settings.HYDRA_PRIVATE_URL}/admin/oauth2/auth/requests/logout/accept"
            response = await client.put(accept_url, params={"logout_challenge": logout_challenge})
            response.raise_for_status()

            data = response.json()
            redirect_to = data.get("redirect_to")
            if not redirect_to:
                logger.error("Missing 'redirect_to' in Hydra response")
                raise HTTPException(status_code=500, detail="Hydra response missing 'redirect_to'")

            logger.info(f"Redirect to: {redirect_to}")
            return JSONResponse(content={"redirect_to": redirect_to})

    except httpx.HTTPStatusError as e:
        logger.exception("Hydra request failed")
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except Exception as e:
        logger.exception("Unexpected error during logout")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/backchannel-logout")
async def backchannel_logout(request: Request):
    form = await request.form()
    logout_token = form.get("logout_token")

    if not logout_token:
        raise HTTPException(status_code=400, detail="Missing logout_token")

    try:
        # Декодируем без верификации (НЕ БЕЗОПАСНО в бою!)
        decoded = jwt.decode(logout_token, options={"verify_signature": False})

        logger.info("🧼 Получен logout_token:")
        logger.info(decoded)

        print("🧼 logout_token (raw claims):")
        print(decoded)

        return {"status": "ok", "claims": decoded}
    except InvalidTokenError as e:
        raise HTTPException(status_code=400, detail=f"Invalid logout_token: {e}")


@router.get("/logout-successful")
async def logout_successful():
    logger.info("Start /logout_successful handler")
    return FileResponse("app/static/logout_successful.html")