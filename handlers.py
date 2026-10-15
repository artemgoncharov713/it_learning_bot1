from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import (
    get_subjects,
    get_topics,
    get_materials,
    get_material,
    get_connection,
)
from keyboards import (
    main_menu_kb,
    back_to_menu_kb,
    subjects_kb,
    topics_kb,
    materials_kb,
    material_card_kb,
)


router = Router()


# ---------- Команды ----------

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        f"Привет, {message.from_user.full_name}!\n\n"
        "Я — IT Learning Bot. Помогаю находить учебные материалы "
        "по дисциплинам и темам, а также сохранять их в избранное.\n\n"
        "Выбери раздел в меню ниже:",
        reply_markup=main_menu_kb()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Как пользоваться ботом:\n\n"
        "• /start — открыть главное меню\n"
        "• /help — эта справка",
        reply_markup=main_menu_kb()
    )


# ---------- Главное меню ----------

@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "Главное меню. Выбери раздел:",
        reply_markup=main_menu_kb()
    )
    await callback.answer()


# ---------- Учебные материалы: список дисциплин ----------

@router.callback_query(F.data == "menu_materials")
async def menu_materials(callback: CallbackQuery):
    subjects = get_subjects()
    if not subjects:
        await callback.message.edit_text(
            "📚 Учебные материалы\n\nПока нет ни одной дисциплины.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📚 Выбери дисциплину:",
        reply_markup=subjects_kb(subjects)
    )
    await callback.answer()


# ---------- Дисциплина → Темы ----------

@router.callback_query(F.data.startswith("subject:"))
async def show_topics(callback: CallbackQuery):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.message.edit_text(
            "📚 В этой дисциплине пока нет тем.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "📖 Выбери тему:",
        reply_markup=topics_kb(topics, subject_id)
    )
    await callback.answer()


# ---------- Тема → Материалы ----------

@router.callback_query(F.data.startswith("topic:"))
async def show_materials(callback: CallbackQuery):
    topic_id = int(callback.data.split(":")[1])
    materials = get_materials(topic_id)
    if not materials:
        await callback.message.edit_text(
            "📖 В этой теме пока нет материалов.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    # Узнаём subject_id для кнопки «К темам»
    conn = get_connection()
    row = conn.execute(
        "SELECT subject_id FROM topics WHERE id = ?", (topic_id,)
    ).fetchone()
    conn.close()
    subject_id = row["subject_id"] if row else 0

    await callback.message.edit_text(
        "📄 Материалы по теме:",
        reply_markup=materials_kb(materials, subject_id)
    )
    await callback.answer()


# ---------- Карточка материала ----------

@router.callback_query(F.data.startswith("material:"))
async def show_material_card(callback: CallbackQuery):
    material_id = int(callback.data.split(":")[1])
    material = get_material(material_id)
    if not material:
        await callback.message.edit_text(
            "❌ Материал не найден.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    # topic_id материала — для кнопки «К материалам»
    conn = get_connection()
    row = conn.execute(
        "SELECT topic_id FROM materials WHERE id = ?", (material_id,)
    ).fetchone()
    conn.close()
    topic_id = row["topic_id"] if row else 0

    text = (
        f"📄 <b>{material['name']}</b>\n\n"
        f"<b>Тип:</b> {material['material_type']}\n"
    )
    if material["description"]:
        text += f"<b>Описание:</b> {material['description']}\n"
    text += f"\n🔗 <a href=\"{material['link']}\">Открыть материал</a>"

    await callback.message.edit_text(
        text,
        reply_markup=material_card_kb(material_id, topic_id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


# ---------- Заглушка для избранного ----------

@router.callback_query(F.data.startswith("fav_add:"))
async def fav_add(callback: CallbackQuery):
    await callback.answer(
        "⭐ Избранное появится на следующем этапе.",
        show_alert=True
    )


# ---------- О боте ----------

@router.callback_query(F.data == "menu_about")
async def menu_about(callback: CallbackQuery):
    await callback.message.edit_text(
        "ℹ️ О боте\n\n"
        "IT Learning Bot помогает студентам находить учебные "
        "материалы по дисциплинам и темам и сохранять их в избранное.\n\n"
        "Технологии: Python, aiogram 3.x, SQLite3.",
        reply_markup=back_to_menu_kb()
    )
    await callback.answer()