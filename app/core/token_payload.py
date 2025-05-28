from typing import Union
import jwt
from jwt import PyJWKClient, ExpiredSignatureError, InvalidTokenError
from app.config import settings


def validate_jwt_with_jwks(token: str) -> Union[dict, str]:
    """
    Валидирует JWT токен через JWKS, получаемый с Hydra по iss из токена.
    Проверка audience отключена.
    """
    try:
        # 1. Получение заголовка и payload без верификации
        headers = jwt.get_unverified_header(token)
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
    except Exception as e:
        return f"Ошибка парсинга токена: {type(e).__name__} — {str(e)}"

    # 2. Получаем issuer из payload
    issuer = unverified_payload.get("iss")
    if not issuer:
        return "Ошибка: в токене отсутствует поле 'iss'"

    # 3. Формируем JWKS URL с подменой localhost на контейнерный адрес
    if "localhost" in issuer:
        jwks_url = f"{settings.HYDRA_URL.rstrip('/')}/.well-known/jwks.json"
    else:
        jwks_url = f"{issuer.rstrip('/')}/.well-known/jwks.json"

    # 4. Получаем ключ из JWKS
    try:
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
    except Exception as e:
        return f"Ошибка получения ключа из JWKS: {str(e)}"

    # 5. Верификация подписи токена, без проверки audience
    try:
        payload = jwt.decode(
            token,
            key=signing_key.key,
            algorithms=[headers["alg"]],
            options={"verify_aud": False},  # <== отключена проверка aud и времени жизни
        )
        return payload
    except ExpiredSignatureError:
        return "Ошибка: срок действия токена истёк"
    except InvalidTokenError as e:
        return f"Ошибка валидации токена: {type(e).__name__} — {str(e)}"
