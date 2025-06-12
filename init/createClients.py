#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.error
import urllib.request
import urllib.parse
import random
import string


def generate_client_name(prefix="Client_", length=8):
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    return prefix + suffix


def generate_scopes():
    base_scopes = ["openid", "offline"]
    optional_scopes = ["oats", "usss", "support_user", "ctn"]
    num_optional = random.randint(0, len(optional_scopes))
    selected_optional = random.sample(optional_scopes, num_optional)
    scopes = base_scopes + selected_optional
    return " ".join(scopes)


def generate_audience():
    return ["MAPIC"] if random.random() < 0.5 else ["MAPIC", "RICH"]


def generate_owner():
    return "owner_" + ''.join(random.choices(string.ascii_lowercase, k=6))


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
                raise
    raise RuntimeError("Слишком много редиректов")


# ---------- ОСНОВНОЙ КОД ----------
def main():
    client_json = {
        "client_name": generate_client_name(),
        "redirect_uris": [
            "http://localhost:3000/redirect-uri",
            "http://localhost:3000/redirect-uri-second"
        ],
        "grant_types": [
            "authorization_code",
            "implicit",
            "refresh_token"
        ],
        "response_types": [
            "code",
            "token",
            "id_token"
        ],
        "client_secret_expires_at": 0,
        "subject_type": "public",
        "userinfo_signed_response_alg": "none",
        "scope": generate_scopes(),
        "audience": generate_audience(),
        "owner": generate_owner(),
        "allowed_cors_origins": [
            "http://127.0.0.1",
            "http://localhost",
            "http://192.168.88.5",
            "http://logbox.myddns.me"
        ],
        "post_logout_redirect_uris": ["http://localhost:3000/logout-successful"],
        "token_endpoint_auth_method": "none",
        "access_token_strategy": "jwt",
        "skip_consent": False,
        "skip_logout_consent": False,
        "frontchannel_logout_session_required": True,
        "backchannel_logout_session_required": True,
        "backchannel_logout_uri": "http://localhost:3000/backchannel-logout",
        "authorization_code_grant_access_token_lifespan": "5m",
        "authorization_code_grant_id_token_lifespan": "60m",
        "authorization_code_grant_refresh_token_lifespan": "48h",
        "client_credentials_grant_access_token_lifespan": "10s",
        "implicit_grant_access_token_lifespan": "10h",
        "implicit_grant_id_token_lifespan": "326340h",
        "jwt_bearer_grant_access_token_lifespan": "100h",
        "refresh_token_grant_id_token_lifespan": "120m",
        "refresh_token_grant_access_token_lifespan": "10m",
        "refresh_token_grant_refresh_token_lifespan": "60h"
    }

    data = json.dumps(client_json).encode('utf-8')
    headers = {"Content-Type": "application/json"}

    result = post_json_with_redirect("http://localhost:4445/admin/clients", data, headers)
    print("Client created:", result.decode())


# ---------- ТОЧКА ВХОДА ----------
if __name__ == '__main__':
    main()
    main()
    main()
