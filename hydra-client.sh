#!/bin/bash
set -e

PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

UVICORN_CMD="uvicorn app.main:app --reload --host 127.0.0.1 --port 3000"

# Проверка, запущен ли uvicorn с app.main:app
PID=$(pgrep -f "$UVICORN_CMD" || true)

if [ -n "$PID" ]; then
    echo "[!] Найден уже запущенный uvicorn:"
    echo "    PID: $PID"
    echo "    Команда: $UVICORN_CMD"
    echo
    echo "Выберите действие:"
    echo "  [1] Завершить процесс"
    echo "  [2] Ничего не делать и выйти"
    read -rp "Ваш выбор (1/2): " CHOICE

    if [ "$CHOICE" == "1" ]; then
        echo "[*] Завершаю процесс $PID..."
        kill "$PID"
        sleep 1
    else
        echo "[*] Отмена запуска."
        exit 0
    fi
fi

# Проверка наличия виртуального окружения
if [ ! -d ".venv" ]; then
    echo "[*] Создаю виртуальное окружение .venv"
    python3 -m venv .venv
fi

# Активация окружения
source .venv/bin/activate

# Установка зависимостей
echo "[*] Устанавливаю зависимости"
pip install --upgrade pip
pip install -r requirements.txt

# Запуск uvicorn
echo "[*] Запуск FastAPI на http://127.0.0.1:3000"
exec $UVICORN_CMD
