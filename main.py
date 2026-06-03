import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from openai import AsyncOpenAI
from dotenv import load_dotenv

# 1. ЗАГРУЗКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ (Дополнительный балл)
# Загружаем ключи из вашего файла. Если вы назвали его api.env, указываем это прямо.
load_dotenv('api.env')

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# 2. ИНИЦИАЛИЗАЦИЯ БОТА
# Используем библиотеку aiogram для создания асинхронного Telegram-бота
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# 3. ИНИЦИАЛИЗАЦИЯ КЛИЕНТА LLM
# Используем библиотеку openai для подключения к OpenRouter (базовый URL изменен на OpenRouter)
client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# Словарь для хранения истории сообщений (Дополнительный балл за контекст диалога)
user_context = {}

# 4. ОБРАБОТЧИКИ КОМАНД БОТА
# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я Telegram-бот с искусственным интеллектом (Gemini Flash). Напиши мне что-нибудь!")

# Обработчик команды /help
@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer("Отправь мне любое сообщение, и я отвечу с помощью нейросети. Бот запоминает контекст нашего диалога. Доступные команды: /start, /help.")

# Обработчик обычных текстовых сообщений
@dp.message(F.text)
async def handle_text(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    # Если пользователь пишет впервые, создаем для него базовую историю
    if user_id not in user_context:
        user_context[user_id] = [{"role": "system", "content": "You are a helpful assistant."}]

    # Добавляем новое сообщение пользователя в историю
    user_context[user_id].append({"role": "user", "content": user_text})

    # Ограничиваем историю 10 последними сообщениями, чтобы не тратить лишние токены
    if len(user_context[user_id]) > 10:
        user_context[user_id] = [user_context[user_id]] + user_context[user_id][-9:]

    try:
        # Отправляем сообщение в LLM, передавая всю историю общения
        response = await client.chat.completions.create(
            model="google/gemini-flash-1.5", # Название вашей модели на OpenRouter
            messages=user_context[user_id]
        )

        # Получаем ответ от ИИ и форматируем его
        bot_reply = response.choices.message.content

        # Сохраняем ответ бота в историю, чтобы он помнил, что сам сказал
        user_context[user_id].append({"role": "assistant", "content": bot_reply})

        # Отправляем ответ пользователю в Telegram
        await message.answer(bot_reply)

    except Exception as e:
        logging.error(f"Ошибка при запросе к LLM: {e}")
        await message.answer("Извините, произошла ошибка при обращении к нейросети. Попробуйте позже.")

# 5. ЗАПУСК БОТА
async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
