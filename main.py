import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from database import init_db
from handlers import router as user_router
from admin import router as admin_router


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.include_router(user_router)
dp.include_router(admin_router)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands)


async def main():
    init_db()  # ← создаёт таблицы subjects/topics/materials/favorites
    bot = Bot(token=BOT_TOKEN)
    await set_commands(bot)
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")