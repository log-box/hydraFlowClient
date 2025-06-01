#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import random
import string
import urllib.error
import urllib.parse
import urllib.request
import logging
from logging.handlers import RotatingFileHandler

# ---------- ЛОГГЕР ----------

LOG_PATH = os.getenv("LOG_PATH", "/init/init_clients.log")
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

logger = logging.getLogger("initClients")
if not logger.handlers:
    logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
    formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")

    # STDOUT
    sh = logging.StreamHandler()
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    # FILE
    fh = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=2)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger.propagate = False  # чтобы не дублировались логи

# ---------- УТИЛИТЫ ----------

def load_env(path, keys):
    try:
        with open(path) as f:
            for line in f:
                if not line.strip() or line.startswith('#'):
                    continue
                k, _, v = line.strip().partition('=')
                if k in keys:
                    os.environ[k] = v
    except Exception as e:
        logger.error("Ошибка загрузки .env: %s", e)
        raise


def get_existing_client_names(admin_url):
    try:
        with urllib.request.urlopen(f"{admin_url}/admin/clients") as resp:
            clients = json.load(resp)
            return {c.get("client_name", "") for c in clients}
    except Exception as e:
        logger.debug("Ошибка получения списка клиентов: %s", e)
        return set()


def generate_unique_name(existing_names, prefix="client_", length=8):
    while True:
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
        name = prefix + suffix
        if name not in existing_names:
            return name


def post_json_with_redirect(url, data, headers, max_redirects=5):
    for _ in range(max_redirects):
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 307:
                redirect_url = e.headers.get("Location")
                if not redirect_url:
                    raise RuntimeError("Redirect (307), но без Location заголовка")
                url = urllib.parse.urljoin(url, redirect_url)
            else:
                logger.warning("Ошибка регистрации: %s %s\n%s", e.code, e.reason, e.read().decode())
                return None
    raise RuntimeError("Слишком много редиректов")


def parse_list_env(varname):
    return [s.strip() for s in os.environ.get(varname, "").split(",") if s.strip()]

# ---------- ОСНОВНОЙ КОД ----------

def main():
    required_vars = {
        "REDIRECT_URI",
        "HYDRA_ADMIN_URL",
        "REDIRECT_URIS"
    }
    load_env('.env', required_vars)

    admin_url = os.environ["HYDRA_ADMIN_URL"].rstrip("/")
    redirect_uris = parse_list_env("REDIRECT_URIS")
    allowed_origins = parse_list_env("ALLOWED_ORIGINS")

    logger.info("redirect_uris: %s", redirect_uris)
    logger.info("allowed_cors_origins: %s", allowed_origins)

    existing_names = get_existing_client_names(admin_url)

    scopes = [
        "openid offline",
        "openid offline usss",
        "openid offline usss oatc"
    ]

    for scope in scopes:
        client_name = generate_unique_name(existing_names)
        existing_names.add(client_name)

        client_json = {
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "grant_types": ["authorization_code", "refresh_token"],
            "response_types": ["code", "id_token"],
            "scope": scope,
            "audience": ["MAPIC", "USSS", "RICH"],
            "owner": "logbox",
            "allowed_cors_origins": allowed_origins,
            "post_logout_redirect_uris": redirect_uris,
            "token_endpoint_auth_method": "none",
            "access_token_strategy": "jwt",
            "skip_consent": False,
            "skip_logout_consent": False,
            "frontchannel_logout_session_required": True,
            "backchannel_logout_session_required": True,
            "backchannel_logout_uri": "http://localhost:3000/redirect-uri/backchannel-logout"
        }

        data = json.dumps(client_json).encode('utf-8')
        headers = {"Content-Type": "application/json"}

        result = post_json_with_redirect(f"{admin_url}/admin/clients", data, headers)
        if result:
            logger.info("Зарегистрирован клиент %s для scope: %s", client_name, scope)

# ---------- ТОЧКА ВХОДА ----------
if __name__ == '__main__':
    main()
