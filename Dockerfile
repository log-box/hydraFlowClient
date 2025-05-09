# Базовый образ с Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем зависимости и устанавливаем их
COPY requirements.txt* ./

# Установка зависимостей
RUN pip install --no-cache-dir --upgrade pip \
 && (pip install -r requirements.txt || poetry install --no-root)

# Копируем всё приложение
COPY . .

# Открываем порт
EXPOSE 3000

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000", "--reload"]