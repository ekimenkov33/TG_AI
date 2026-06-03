FROM python:3.13-slim

# Создаем и делаем активной рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файл с зависимостями проекта
COPY requirements.txt .

# Устанавливаем необходимые зависимости (aiogram, openai, python-dotenv) без кэширования
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все остальные файлы приложения (main.py и др.) в образ
COPY . .

# Определяем команду, которая автоматически запустит бота при старте контейнера
CMD ["python", "main.py"]
