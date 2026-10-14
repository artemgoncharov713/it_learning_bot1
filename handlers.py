from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from keyboards import back_to_menu_kb, main_menu_kb

router = Router()


# ---------- Команды ----------


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n\n"
        "Я — IT Learning Bot. Помогаю находить учебные материалы "
        "по дисциплинам и темам, а также сохранять их в избранное.\n\n"
        "Выбери раздел в меню ниже:",
        reply_markup=main_menu_kb(),
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "• /start — открыть главное меню\n"
        "• /help — эта справка\n\n"
        "Разделы меню:\n"
        "📚 Учебные материалы — каталог дисциплин и тем\n"
        "🔍 Поиск материалов — поиск по названию\n"
        "⭐ Избранное — сохранённые материалы\n"
        "ℹ️ О боте — информация о проекте",
        reply_markup=main_menu_kb(),
    )


# ---------- Главное меню ----------


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню. Выбери раздел:", reply_markup=main_menu_kb()
    )
    await callback.answer()


# ---------- Учебные материалы ----------


@router.callback_query(F.data == "menu_materials")
async def menu_materials(callback: CallbackQuery):
    await callback.message.edit_text(
        "📚 Учебные материалы\n\n"
        "Здесь будет список дисциплин.\n"
        "(Появится на этапе 4.)",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


# ---------- Поиск ----------


@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    await callback.message.edit_text(
        "🔍 Поиск материалов\n\n"
        "Здесь можно будет искать материалы по названию.\n"
        "(Появится на этапе 5.)",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


# ---------- Избранное ----------


@router.callback_query(F.data == "menu_favorites")
async def menu_favorites(callback: CallbackQuery):
    await callback.message.edit_text(
        "⭐ Избранное\n\n"
        "Здесь будут материалы, которые ты сохранил.\n"
        "(Появится на этапе 5.)",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


# ---------- О боте ----------


@router.callback_query(F.data == "menu_about")
async def menu_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О боте\n\n"
        "IT Learning Bot помогает студентам находить учебные "
        "материалы по дисциплинам и темам и сохранять их в избранное.\n\n"
        "Технологии: Python, aiogram 3.x, SQLite3.",
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()