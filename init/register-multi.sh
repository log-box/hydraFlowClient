#!/bin/bash
set -e

# Загрузка переменных из .env
set -a
. /init/.env
set +a

SCOPES=("openid offline" "openid offline usss" "openid offline usss oatc")

for i in "${!SCOPES[@]}"; do
  export REDIRECT_URI="${REDIRECT_URI_COMPOSE}"
  export ALLOWED_ORIGIN="${ALLOWED_ORIGIN_COMPOSE}"
  export HYDRA_ADMIN_URL="${HYDRA_ADMIN_URL_COMPOSE}"
  export SCOPE="${SCOPES[$i]}"

  envsubst < init/client.template.json > init/client.json

  curl -s -o /dev/null -w "%{http_code}" -X POST "$HYDRA_ADMIN_URL/clients" \
    -H "Content-Type: application/json" \
    -d @init/client.json

  echo "Client $CLIENT_ID зарегистрирован с scope: $SCOPE"

  rm -f init/client.json
done
