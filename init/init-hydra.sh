#!/bin/sh
#set -e
#
#echo "⏳ Ждём готовности Hydra..."
#until curl -sf http://hydra:4445/health/ready; do
#  sleep 1
#done
#
#echo "✅ Hydra готова. Создаём клиентов..."
#
#hydra clients create \
#  --endpoint http://hydra:4445 \
#  --id my-client \
#  --secret my-secret \
#  --grant-types authorization_code,refresh_token \
#  --response-types code,id_token \
#  --scope openid,offline \
#  --redirect-uris http://localhost:3000/redirect-uri \
#  --token-endpoint-auth-method client_secret_post || true
#
#hydra clients create \
#  --endpoint http://hydra:4445 \
#  --id my-client-second \
#  --secret my-secret-second \
#  --grant-types authorization_code,refresh_token \
#  --response-types code,id_token \
#  --scope openid,offline \
#  --redirect-uris http://localhost:3000/redirect-uri-second \
#  --token-endpoint-auth-method client_secret_post || true
#
#echo "✅ Готово."



##################
#!/bin/bash
set -e

# Подгружаем переменные
set -a
. /init/.env
set +a

echo "⏳ Ждём готовности Hydra..."
until curl -sf "${HYDRA_ADMIN_URL:-http://hydra:4445}/health/ready"; do
  sleep 1
done

echo "🚀 Регистрируем клиентов..."
/bin/bash /init/register-multi.sh

# (опционально) Ещё один клиент — вручную:
echo "⚙️ Генерируем client.json..."
/init/generate-client.sh

echo "📤 POST клиент из client.json..."
curl -s -X POST ${HYDRA_ADMIN_URL:-http://hydra:4445}/admin/clients \
     -H "Content-Type: application/json" \
     -d @/init/client.json

rm -f /init/client.json
echo "✅ Всё готово."
