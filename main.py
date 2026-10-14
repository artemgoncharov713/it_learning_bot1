import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n\n"
        "Я — IT Learning Bot. Помогаю находить учебные материалы "
        "по дисциплинам и темам, а также сохранять их в избранное.\n\n"
        "Доступные команды:\n"
        "/start — запустить бота\n"
        "/help — краткая справка"
    )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "• /start — открыть главное меню\n"
        "• /help — эта справка\n\n"
        "Скоро появятся разделы «Учебные материалы», "
        "«Поиск» и «Избранное»."
    )


async def main():
    bot = Bot(token=BOT_TOKEN)
    print("Бот запущен. Нажмите Ctrl+C для остановки.")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен.")