#!/bin/sh
set -e

# Поддержка переменных по умолчанию
: "${CLIENT_ID:=my-client}"
: "${CLIENT_NAME:=My Client}"
: "${CLIENT_SECRET:=super-secret}"
: "${REDIRECT_URI:=http://localhost:3000/redirect-uri}"
: "${ALLOWED_ORIGIN:=http://localhost:3000}"

envsubst < /init/client.template.json > /init/client.json
