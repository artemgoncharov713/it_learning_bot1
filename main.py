import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import router
from admin import admin_router


logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.include_router(router)
dp.include_router(admin_router)


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Главное меню"),
        BotCommand(command="help", description="Справка"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_TOKEN)
    await set_commands(bot)
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")