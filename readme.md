# Hydra Flow Client

**Hydra Flow Client** — это FastAPI-приложение с HTML/JS-интерфейсом для интерактивного тестирования OAuth2/OIDC-флоу через ORY Hydra. Предназначено для ручного прохождения сценариев входа, согласия и выхода с возможностью конфигурации параметров "на лету" через UI. Заменяет Postman при работе с Hydra и предоставляет автоматизированный, визуальный контроль над передачей параметров, формированием токенов и редиректов.

---

## ⚙️ Назначение

* UI + backend для ручного запуска `authorization_code` флоу в Hydra
* Ввод параметров логина/консента вручную через HTML-формы
* Отображение и валидация токенов (JWT)
* Поддержка ошибок `error`/`error_description` для проверки отказов
* Вариативные redirect-uri для проверки сценариев

---

## 📂 Структура проекта

```
.
├── app/
│   ├── api/                   # Эндпоинты FastAPI: login, consent, logout, redirect
│   ├── core/                  # Взаимодействие с Hydra, сессии, payload
│   ├── static/                # HTML-страницы (login.html, consent.html и др.)
│   ├── templates/             # Шаблоны Jinja (например, redirect_result)
│   ├── main.py                # Точка входа FastAPI
│   ├── config.py              # Работа с .env и in-memory настройками
│   ├── logger.py              # Логирование
│   └── schemas.py             # Pydantic-схемы
├── hydra/config/hydra.yml     # Конфигурация ORY Hydra
├── init/
│   ├── client.template.json   # Шаблон клиента Hydra
│   ├── generate-client.sh     # Генерация client.json из переменных
│   └── init-hydra.sh          # Регистрация клиента в Hydra
├── .env                       # Конфигурация окружения (для FastAPI)
├── Dockerfile                 # Сборка образа клиента
├── docker-compose.yml         # FastAPI + Hydra + Postgres + Init
└── readme.md                  # Вы здесь
```

---

## 🚀 Быстрый старт (локально)

```bash
docker-compose up --build
```

Доступные сервисы:

* UI клиента: [http://localhost:3000](http://localhost:3000)
* Hydra Admin API: [http://localhost:4445](http://localhost:4445)
* Hydra Public API: [http://localhost:4444](http://localhost:4444)

---

## 🧠 Хранение состояния

Состояние сессии (login, consent, subject, claims) хранится **в оперативной памяти** на основе переменных в `config.py`.

* При входе (`/login`) настройки заполняются из параметров формы
* При согласии (`/consent`) используется текущий контекст
* Настройки можно сбросить, активировать флаги `remember`, `extend_lifespan`, изменить ID, scope и др.

**Сторонние хранилища не используются** — Redis, cookie и БД не применяются.

---

## 📋 Маршруты

| URL                              | Описание                                   |
| -------------------------------- | ------------------------------------------ |
| `/login?login_challenge=...`     | Форма входа (интерактивная)                |
| `/consent?consent_challenge=...` | Форма согласия                             |
| `/logout?logout_challenge=...`   | Завершение сессии                          |
| `/redirect-uri`                  | Получение токенов / отображение результата |
| `/redirect-uri-second`           | Альтернативный redirect для тестов         |

Дополнительно:

* Поддержка **отказа с ошибкой** через поля `error` и `error_description`
* Валидация токенов (access, ID) как JWT (в UI)

---

## 🔧 REST API (вспомогательные)

Эндпоинты для загрузки и отправки данных с фронта:

| Метод  | Эндпоинт            | Назначение                        |
| ------ | ------------------- | --------------------------------- |
| `GET`  | `/login_settings`   | Получить текущие настройки логина |
| `POST` | `/login_process`    | Подтвердить логин / отказаться    |
| `GET`  | `/consent_settings` | Получить текущие параметры        |
| `POST` | `/consent_process`  | Подтвердить consent / отказаться  |

---

## 📄 Переменные окружения (`.env`)

Ключевые параметры:

```env
# Hydra API
HYDRA_URL=http://hydra:4444
HYDRA_PRIVATE_URL=http://hydra:4445
HYDRA_OUTSIDE_URL=http://localhost:4444

# Клиент
CLIENT_ID=...
CLIENT_SECRET=...
REDIRECT_URI=/redirect-uri
POST_LOGOUT_REDIRECT_URI=/logout

# Параметры логина
LOGIN_SUBJECT=...
LOGIN_CREDENTIAL=...
LOGIN_ACR=...
LOGIN_AMR=...
LOGIN_CONTEXT={"DEFAULT":"DEFAULT"}
EXTEND_SESSION_LIFESPAN=true
REMEMBER=true
REMEMBER_FOR=0

# Параметры consent
CONSENT_CONTEXT={"DEFAULT":"DEFAULT"}
GRANT_SCOPE=openid,offline
GRANT_ACCESS_TOKEN_AUDIENCE=MAPIC
SESSION_ID_TOKEN={"login":"DEFAULT"}
SESSION_ACCESS_TOKEN={"identity_id":"DEFAULT"}
```

Все параметры можно переопределить на этапе логина и согласия через интерфейс.

---

## 🛠 В разработке

* В будущем возможно добавление:

  * тестов (`pytest`, `httpx`)
  * Helm-чарта для Kubernetes
  * миграций и seed-данных
