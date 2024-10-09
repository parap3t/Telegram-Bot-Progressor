# Импортируем недостающие модули
import logging
from aiogram import Bot, Dispatcher
from bot.user import user
from bot.admin import admin
from asyncio import run
from database.models import async_main
from config import BOT_API

# Запуск бота

logging.basicConfig(level=logging.INFO)


async def main() -> None:
    await async_main()
    bot = Bot(token=BOT_API)  # Взаимодействие с ботом
    dp = Dispatcher()  # Получение обновлений бота
    dp.include_routers(admin, user)
    await dp.start_polling(bot)

# Запуск программы
if __name__ == "__main__":  # Создаём точку входа
    try:
        # Уведомляем о запуске бота
        print("Бот включён!")
        run(main())
        # Обработаем выключение бота
    except KeyboardInterrupt:
        print("Бот выключен!")
