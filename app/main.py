import httpx
from fastapi import FastAPI
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles

from app.api import login, logout, consent, redirect
from app.config import settings
from app.logger import logger
import os, json, base64, hashlib, uuid

app = FastAPI()
app.include_router(login.router)
app.include_router(logout.router)
app.include_router(consent.router)
app.include_router(redirect.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
logger.info("Starting hydraFlowClient app")


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
    return FileResponse(
        path="app/static/favicon.ico",
        media_type="image/x-icon",
        headers={"Cache-Control": "public, max-age=86400"}
    )

@app.get("/sitemap.xml")
async def sitemap():
    xml_stub = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"></urlset>
"""
    return Response(
        content=xml_stub,
        media_type="application/xml",
        headers={"Cache-Control": "public, max-age=86400"}
    )

def b64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).decode().rstrip("=")

@app.post("/proxy/pkce/prefill")
async def pkce_prefill():
    # verifier 64 байта → ~86 символов base64url
    code_verifier = b64url(os.urandom(64))
    code_challenge = b64url(hashlib.sha256(code_verifier.encode()).digest())
    raw_state = str(uuid.uuid4())
    state_obj = {"s": raw_state, "v": code_verifier}
    state = b64url(json.dumps(state_obj, separators=(",",":")).encode())
    return {"state": state, "code_verifier": code_verifier, "code_challenge": code_challenge}
