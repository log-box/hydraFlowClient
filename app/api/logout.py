from app.config import settings
from fastapi import HTTPException, APIRouter
from fastapi.responses import FileResponse, JSONResponse
import logging
import httpx

router = APIRouter()
logger = logging.getLogger("hydraApp")
@router.get("/logout")
async def serve_logout_page():
    return FileResponse("app/static/logout.html")


@router.get("/logout_process")
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
