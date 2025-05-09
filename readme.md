# Hydra Flow Client

Этот проект поднимает тестовую инфраструктуру на базе **ORY Hydra** и клиента **FastAPI** для разработки и отладки флоу получения токенов (OAuth2 / OpenID Connect).

---

## 📦 Структура проекта

```bash
hydraFlowClient/
├── app/                  # FastAPI-приложение (login, consent, redirect)
├── hydra/config/         # Конфигурация Hydra (hydra.yml)
├── init/                 # Скрипты инициализации Hydra (создание клиентов)
├── static/               # HTML-шаблоны (включая auth form)
├── Dockerfile            # Сборка образа FastAPI
├── docker-compose.yml    # Запуск всей инфраструктуры
├── requirements.txt      # Зависимости FastAPI
├── .env                  # Переменные окружения FastAPI
```

---

## 🚀 Быстрый старт

1. Клонируй репозиторий:

```bash
git clone <repo-url>
cd hydraFlowClient
```

2. Собери и запусти:

```bash
docker compose up --build
```

3. Доступные интерфейсы:

- Hydra Public (OIDC): [http://localhost:4444](http://localhost:4444)
- Hydra Admin: [http://localhost:4445](http://localhost:4445)
- FastAPI клиент: [http://localhost:3000](http://localhost:3000)

---

## 🧪 Проверка OAuth2 флоу через браузер

Интерактивная форма доступна по адресу:

📍 [http://localhost:3000](http://localhost:3000)

### ✅ Как работает:

1. Выберите клиента и его `redirect_uri` в форме.
2. Укажите `scope`, `state`, `nonce`, `response_type=code`.
3. Нажмите кнопку **«Перейти по ссылке»**.
4. Пройдёт весь OAuth2 флоу:
   - переход в `/login`
   - подтверждение в `/consent`
   - редирект на `/redirect-uri` или `/redirect-uri-second`
5. ✅ В результате вы получите `access_token`, `id_token`, `refresh_token` в JSON в браузере.

---

## ⚠️ Ограничения

- Поддерживаются **2 клиента** с фиксированными redirect URI.
- Их параметры нужно прописывать вручную в `.env`.

Пример `.env`:

```env
CLIENT_ID=TestClient1
CLIENT_ID_SECOND=TestClient2
REDIRECT_URI=http://localhost:3000/redirect-uri
REDIRECT_URI_SECOND=http://localhost:3000/redirect-uri-second

HYDRA_URL=http://localhost:4444
HYDRA_PRIVATE_URL=http://localhost:4445
```

---

## 📚 Зависимости

- [ORY Hydra](https://www.ory.sh/hydra/)
- FastAPI, Uvicorn, HTTPX
- PostgreSQL

---

## 🧹 Остановка и очистка

```bash
docker compose down -v
```

---

## 📝 Лицензия

MIT License


---

## 🛠️ Автозапуск через systemd

Для автоматического запуска FastAPI-клиента в контейнере при входе пользователя используется `systemd` юзер-сервис.

Файлы:

- `hydra-client.service` — юнит-файл для systemd:  
  размещается в:  
  ```bash
  ~/.config/systemd/user/hydra-client.service
  ```

  Содержимое:

  ```ini
  [Unit]
  Description=HydraClient FastAPI App
  After=network.target

  [Service]
  Type=simple
  ExecStart=/home/$USER/programming/hydraFlowClient/hydra-client-docker.sh
  WorkingDirectory=/home/$USER/programming/hydraFlowClient
  Restart=on-failure

  [Install]
  WantedBy=default.target
  ```

- `hydra-client-docker.sh` — скрипт запуска:

  ```bash
  #!/bin/bash
  cd "$(dirname "$0")"
  docker compose up --build --remove-orphans
  ```

### ▶️ Команды управления:

```bash
systemctl --user daemon-reload
systemctl --user enable --now hydra-client.service
```

Проверь статус:

```bash
systemctl --user status hydra-client.service
```

