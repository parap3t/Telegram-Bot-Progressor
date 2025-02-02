import bot.config as cfg

from aiogram import Dispatcher
from bot.user import user
from bot.admin import admin
from asyncio import run
from database.models import async_main


async def main() -> None:
    
    await async_main()
    
    dp = Dispatcher() # Получение обновлений бота
    dp.include_routers(admin,user)
    
    await dp.start_polling(cfg.BOT)


if __name__ == "__main__": 
    
    try:
        
        print("Бот включён!")
        run(main())

    except KeyboardInterrupt:
        print("Бот выключен!")
        