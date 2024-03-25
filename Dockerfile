# Использую официальный образ Python
FROM python:3.9-slim-buster

# Установите зависимости для psycopg2 и установите его
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Копирую файлы с зависимостями и устанавливаю их
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Коипрую остальные файлы проекта
COPY . /app
WORKDIR /app/fit_bot

# Устанавливаю переменные окружения
ENV PYTHONPATH /app:$PYTHONPATH
ENV DJANGO_SETTINGS_MODULE=fit_bot.settings
ENV PORT 8000
ENV TZ=Europe/Moscow


# Запускаю приложение
CMD gunicorn fit_bot.wsgi:application --bind localhost:$PORT