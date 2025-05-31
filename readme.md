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

## 📦 ИНСТРУКЦИЯ ПО УСТАНОВКЕ

### 📁 Шаг 1. Клонирование

```bash
git clone https://github.com/log-box/hydraFlowClient.git
cd hydraFlowClient
```

---

### ⚙️ Шаг 2. Настройка `.env`

Создайте `.env` в корне проекта, ориентируясь на `.env.template`.

Минимально:

```ini
# Внешние адреса (те, которые будут использоваться в браузере)
HYDRA_PUBLIC_URL=https://hydra.example.com
CLIENT_REDIRECT_URL=http://localhost:3000/callback
CLIENT_FRONT_URL=http://localhost:3000

# Локальные порты
HOST_PORT=3000
```

Пояснение:

* `HYDRA_PUBLIC_URL` — публичный адрес ORY Hydra (доступный из браузера).
* `CLIENT_REDIRECT_URL` — адрес, на который Hydra сделает редирект после login/consent.
* `CLIENT_FRONT_URL` — адрес самого клиента (веб-интерфейса).
* `HOST_PORT` — порт, на котором будет доступен frontend (localhost:3000).

---

### 🐳 Шаг 3. Установка Docker Compose v2+

Проверь версию:

```bash
docker compose version
```

Если ошибка или версия ниже 2.x:

**Для Linux (с systemd):**

```bash
sudo apt-get update
sudo apt-get install docker-compose-plugin
```

Проверка:

```bash
docker compose version
```

---

### ▶️ Шаг 4. Запуск

```bash
docker compose up --build
```

---

### ✅ Шаг 5. Открытие в браузере

Интерфейс будет доступен по адресу:

```
http://localhost:3000
```
