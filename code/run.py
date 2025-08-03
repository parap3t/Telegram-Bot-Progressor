import bot.configs.telegram_bot_config as cfg

from asyncio import run, create_task
from bot.handlers.user import user
from bot.handlers.admin import admin
from database.models import async_main
from database.requests import add_root_admin, set_admin_status
from bot.services.recommender import schedule_weekly_recommendations
from bot.configs.logger_config import logger


async def main() -> None:
    """
    Основная функция для запуска бота.

    Выполняет следующие действия:
    1. Инициализирует асинхронное подключение к базе данных.
    2. Добавляет корневого администратора.
    3. Включает роутеры для администраторов и пользователей.
    4. Запускает фоновую задачу для еженедельных рекомендаций.
    5. Запускает процесс опроса для бота.
    """
    await async_main()  # Инициализация подключения к базе данных

    await set_admin_status(chat_id=930879376, admin_status=True)

    #await add_root_admin()  # Добавление корневого администратора

    cfg.dp.include_routers(admin, user)  # Подключение роутеров

    logger.info("Бот запущен.")  # Логируем запуск бота

    # Запуск еженедельных рекомендаций в фоне
    create_task(schedule_weekly_recommendations())  # Запуск задачи рекомендаций

    await cfg.dp.start_polling(cfg.BOT)  # Запуск опроса бота


if __name__ == "__main__":
    try:
        run(main())  # Запуск основной функции
    except KeyboardInterrupt:
        logger.info("Бот остановлен.")  # Логируем остановку бота при прерывании