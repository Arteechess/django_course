FROM python:3.11-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем необходимые зависимости
RUN apt-get update && apt-get install -y \
    sqlite3 libsqlite3-dev

# Устанавливаем pip и зависимости из requirements.txt
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Копируем исходный код
COPY . .
