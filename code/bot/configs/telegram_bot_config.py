import os
from aiogram import Bot
from aiogram import Dispatcher
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Создание экземпляра бота с использованием токена из переменной окружения
BOT = Bot(token=os.getenv("BOT_API"))

# Создание экземпляра диспетчера для обработки входящих сообщений
dp = Dispatcher()
