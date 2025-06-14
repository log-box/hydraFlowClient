
# Hydra Flow Client

## Описание

**Hydra Flow Client** — это интерфейс для тестирования OAuth2-сценариев на базе [ORY Hydra](https://www.ory.sh/hydra/). Поддерживает `Authorization Code Flow` с полноценной обработкой login / consent / logout через веб-интерфейс.

Реализован как **UI-клиент**, а не API: используется визуальная форма логина, окно согласия, страницы завершения сессии и отладки токенов.

---

## Требования

- Docker
- **Docker Compose версии 2 или выше**

Проверить:
```bash
docker compose version
```

Если у вас используется `docker-compose` с дефисом, обновитесь до [Compose v2](https://docs.docker.com/compose/install/linux/).

---

## Запуск

```bash
git clone https://your-repo-url/hydraFlowClient.git
cd hydraFlowClient
cp .env.example .env
docker compose up --build
```

Интерфейс будет доступен по адресу:  
📍 `http://localhost:8000/login`

---

## UI-интерфейс

Веб-интерфейс включает следующие страницы:
- Страницу инициализации запроса
- Страницу loginRequest
- Страницу consentRequest
- Страницу витрины, с полученными токенами или ошибкой
  - Валидация JWT реализована
- Страницу logoutRequest
- Страницу postLogoutRedirect

---

## Структура проекта

```
hydraFlowClient/
├── .env
├── docker-compose.yml
├── Dockerfile
├── app/
│   ├── main.py
│   ├── config.py
│   ├── logger.py
│   ├── schemas.py
│   ├── api/
│   │   ├── login.py
│   │   ├── consent.py
│   │   ├── logout.py
│   │   └── redirect.py
│   ├── core/
│   │   ├── context.py
│   │   ├── context_storage.py
│   │   ├── hydra.py
│   │   ├── token_payload.py
│   │   └── database.py
│   ├── static/
│   │   ├── login.html
│   │   ├── consent.html
│   │   ├── logout.html
│   │   └── logout_successful.html
│   └── templates/
│       └── redirect_result.html.jinja
├── hydra/config/hydra.yml
├── init/createClients.py
├── nginx/etc/nginx/conf.d/
├── logs/
```

---

## Тестирование сценариев

Hydra Flow Client можно использовать для ручной отладки:

- Получения токенов через браузер
- Проверки работы logout и очистки сессий
- Визуального анализа JWT payload
- Демонстрации `auth code flow` с UI-интерфейсом

Готовый сервис можно протестировать по [ссылке](http://logbox.myddns.me:3001)