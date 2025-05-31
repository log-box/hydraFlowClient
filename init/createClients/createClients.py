#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import urllib.request
import urllib.error
import urllib.parse
import random
import string

def load_env(path, keys):
    with open(path) as f:
        for line in f:
            if not line.strip() or line.startswith('#'):
                continue
            k, _, v = line.strip().partition('=')
            if k in keys:
                os.environ[k] = v

def get_existing_client_names(admin_url):
    try:
        with urllib.request.urlopen(f"{admin_url}/admin/clients") as resp:
            clients = json.load(resp)
            return {c.get("client_name", "") for c in clients}
    except Exception as e:
        print("Ошибка получения списка клиентов:", e)
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
                print(f"Ошибка регистрации: {e.code} {e.reason}")
                print(e.read().decode())
                return None
    raise RuntimeError("Слишком много редиректов")
    
def parse_list_env(varname):
    return [s.strip() for s in os.environ.get(varname, "").split(",") if s.strip()]
    
def main():

    required_vars = {
        "REDIRECT_URI",
        "ALLOWED_ORIGIN",
        "HYDRA_ADMIN_URL",
        "REDIRECT_URIS"
    }
    load_env('.env', required_vars)
    admin_url = os.environ["HYDRA_ADMIN_URL"]
    redirect_uris = parse_list_env("REDIRECT_URIS")
    existing_names = get_existing_client_names(admin_url)
    print(redirect_uris)
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
            "allowed_cors_origins": ["http://localhost:3000"],
            "post_logout_redirect_uris": ["http://localhost:3000","http://192.168.88.5:3000","http://127.0.0.1:3000"],
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
            print(f"Зарегистрирован: {client_name} (scope: {scope})")

if __name__ == '__main__':

    main()

