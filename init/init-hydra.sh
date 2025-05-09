#!/bin/sh
set -e

echo "⏳ Ждём готовности Hydra..."
until curl -sf http://hydra:4445/health/ready; do
  sleep 1
done

echo "✅ Hydra готова. Создаём клиентов..."

hydra clients create \
  --endpoint http://hydra:4445 \
  --id my-client \
  --secret my-secret \
  --grant-types authorization_code,refresh_token \
  --response-types code,id_token \
  --scope openid,offline \
  --redirect-uris http://localhost:3000/redirect-uri \
  --token-endpoint-auth-method client_secret_post || true

hydra clients create \
  --endpoint http://hydra:4445 \
  --id my-client-second \
  --secret my-secret-second \
  --grant-types authorization_code,refresh_token \
  --response-types code,id_token \
  --scope openid,offline \
  --redirect-uris http://localhost:3000/redirect-uri-second \
  --token-endpoint-auth-method client_secret_post || true

echo "✅ Готово."
