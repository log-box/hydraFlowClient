import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api import login, logout, consent, redirect
from app.config import settings
from app.logger import logger

app = FastAPI()
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(consent.router)
app.include_router(redirect.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def serve_form():
    logger.info("Start / handler")
    return FileResponse("app/static/auth_form.html")


@app.get("/proxy/clients")
async def proxy_clients():
    logger.info("Start /proxy/clients handler")
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{settings.HYDRA_PRIVATE_URL}/admin/clients")
        response.raise_for_status()
        return response.json()


@app.get("/favicon.ico")
async def favicon():
    return Response(
        content=b"",
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=86400"}
    )
