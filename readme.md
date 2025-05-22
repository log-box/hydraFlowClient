Отлично, структура теперь ясна. Обновлённый `README.md` для репозитория `hydraFlowClient` с учётом текущей архитектуры и логики будет таким:

---

# Hydra Flow Client

FastAPI-приложение, реализующее кастомные формы входа, согласия и логаута для ORY Hydra с возможностью ручной настройки параметров. Предназначено для интеграции в архитектуру OAuth2/OpenID Connect, работает в связке с Hydra.

## 📦 Структура проекта

```
.
├── app
│   ├── api                 # FastAPI роутеры: login, consent, logout, redirect
│   ├── core                # Взаимодействие с Hydra (core/hydra.py)
│   ├── static              # HTML-формы: login.html, consent.html и др.
│   ├── config.py           # Загрузка конфигурации из окружения
│   ├── logger.py           # Настройка логирования
│   ├── main.py             # Точка входа FastAPI
│   └── schemas.py          # Pydantic-схемы
├── hydra
│   └── config
│       └── hydra.yml       # Конфигурация ORY Hydra
├── init
│   └── init-hydra.sh       # Инициализация клиентов Hydra
├── .env                    # Переменные окружения для FastAPI
├── Dockerfile              # Сборка приложения
├── docker-compose.yml      # Поднятие Hydra, Postgres и FastAPI
├── hydra-client.service    # Systemd unit (опционально)
├── hydra-client-docker.sh  # Скрипт запуска из Docker
├── requirements.txt
└── readme.md               # Вы здесь 📖
```

## 🚀 Запуск

```bash
docker-compose up --build
```

По умолчанию сервисы доступны на портах:

* FastAPI UI: [http://localhost:3000](http://localhost:3000)
* Hydra Admin: [http://localhost:4445](http://localhost:4445)
* Hydra Public: [http://localhost:4444](http://localhost:4444)

## 🔐 Переменные окружения (`.env`)

```env
HYDRA_URL=http://hydra:4444
HYDRA_PRIVATE_URL=http://hydra:4445
HYDRA_OUTSIDE_URL=http://localhost:4444

CLIENT_ID=...
CLIENT_ID_SECOND=...
REDIRECT_URI=...
POST_LOGOUT_REDIRECT_URI=...

LOGIN_SUBJECT=...
LOGIN_CREDENTIAL=...
LOGIN_ACR=...
LOGIN_AMR=...
LOGIN_CONTEXT={"key": "value"}
EXTEND_SESSION_LIFESPAN=true
REMEMBER=true
REMEMBER_FOR=0

CONSENT_CONTEXT={"key": "value"}
GRANT_ACCESS_TOKEN_AUDIENCE=...
GRANT_SCOPE=openid,offline
SESSION_ID_TOKEN={"claim": "value"}
SESSION_ACCESS_TOKEN={"claim": "value"}
```

## 📋 Формы

* `/login?login_challenge=...` – форма входа
* `/consent?consent_challenge=...` – форма согласия
* `/logout?logout_challenge=...` – форма выхода
* `/redirect-uri` – точка получения токена и отображения результата

Поддерживается ручной ввод JSON-полей и пользовательский отказ с заданием `error` и `error_description`.

## 💬 API

FastAPI-эндпоинты:

* `GET /login_settings` – получить дефолтные значения для формы входа
* `POST /login_process` – обработка логина или отказа
* `GET /consent_settings` – получить настройки согласия
* `POST /consent_process` – обработка согласия или отказа
* `GET /logout` – форма логаута
* `GET /redirect-uri` – финальный редирект после логина или ошибки

## 🛠 Dev Notes

* Статика монтируется по пути `/static`
* Uvicorn запускается с `--reload` для hot-reload
* Приложение разделено на API (по видам взаимодействий) и Core (логика с Hydra)

## 🧪 Тестирование

Для имитации отказа достаточно нажать "Отмена" и задать поля `error` и `error_description`. Они будут переданы Hydra и отрендерены в `/redirect-uri`.

---

Нужна также версия на английском — скажи, и подготовлю.
