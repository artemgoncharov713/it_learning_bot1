from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from database import (
    get_subjects,
    get_topics,
    get_materials,
    get_material,
    get_connection,
    search_materials,
    add_to_favorites,
    get_favorites,
    remove_from_favorites,
)
from keyboards import (
    main_menu_kb,
    back_to_menu_kb,
    subjects_kb,
    topics_kb,
    materials_kb,
    material_card_kb,
    search_results_kb,
    favorites_kb,
    fav_material_card_kb,
)


router = Router()

# Хранилище ожидающих поиска
search_waiting = set()


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
        "• /help — эта справка\n\n"
        "Разделы меню:\n"
        "📚 Учебные материалы — каталог дисциплин и тем\n"
        "🔍 Поиск материалов — поиск по названию\n"
        "⭐ Избранное — сохранённые материалы\n"
        "ℹ️ О боте — информация о проекте",
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

    if material["video_link"]:
        text += f"\n📺 <a href=\"{material['video_link']}\">Видеоурок в канале</a>"

    await callback.message.edit_text(
        text,
        reply_markup=material_card_kb(material_id, topic_id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


# ---------- Избранное: добавление ----------

@router.callback_query(F.data.startswith("fav_add:"))
async def fav_add(callback: CallbackQuery):
    material_id = int(callback.data.split(":")[1])
    added = add_to_favorites(callback.from_user.id, material_id)

    if added:
        await callback.answer("⭐ Добавлено в избранное")
    else:
        await callback.answer("Уже в избранном")


# ---------- Избранное: список ----------

@router.callback_query(F.data == "menu_favorites")
async def menu_favorites(callback: CallbackQuery):
    favorites = get_favorites(callback.from_user.id)

    if not favorites:
        await callback.message.edit_text(
            "⭐ <b>Избранное</b>\n\n"
            "Здесь пока пусто. Добавляй материалы звёздочкой ⭐ "
            "из карточки материала.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"⭐ <b>Избранное</b>\n\nСохранено материалов: {len(favorites)}",
        reply_markup=favorites_kb(favorites),
        parse_mode="HTML"
    )
    await callback.answer()


# ---------- Избранное: просмотр материала ----------

@router.callback_query(F.data.startswith("fav_view:"))
async def fav_view(callback: CallbackQuery):
    material_id = int(callback.data.split(":")[1])
    material = get_material(material_id)

    if not material:
        await callback.message.edit_text(
            "❌ Материал не найден.",
            reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    text = (
        f"⭐ <b>{material['name']}</b>\n\n"
        f"<b>Тип:</b> {material['material_type']}\n"
    )
    if material["description"]:
        text += f"<b>Описание:</b> {material['description']}\n"

    text += f"\n🔗 <a href=\"{material['link']}\">Открыть материал</a>"

    if material["video_link"]:
        text += f"\n📺 <a href=\"{material['video_link']}\">Видеоурок в канале</a>"

    await callback.message.edit_text(
        text,
        reply_markup=fav_material_card_kb(material_id),
        parse_mode="HTML",
        disable_web_page_preview=True
    )
    await callback.answer()


# ---------- Избранное: удаление ----------

@router.callback_query(F.data.startswith("fav_del:"))
async def fav_del(callback: CallbackQuery):
    material_id = int(callback.data.split(":")[1])
    removed = remove_from_favorites(callback.from_user.id, material_id)

    if removed:
        await callback.answer("Удалено из избранного")
    else:
        await callback.answer("Не найдено в избранном")

    favorites = get_favorites(callback.from_user.id)

    if not favorites:
        await callback.message.edit_text(
            "⭐ <b>Избранное</b>\n\nПусто.",
            reply_markup=back_to_menu_kb(),
            parse_mode="HTML"
        )
        return

    await callback.message.edit_text(
        f"⭐ <b>Избранное</b>\n\nСохранено материалов: {len(favorites)}",
        reply_markup=favorites_kb(favorites),
        parse_mode="HTML"
    )


# ---------- Поиск ----------

@router.callback_query(F.data == "menu_search")
async def menu_search(callback: CallbackQuery):
    search_waiting.add(callback.from_user.id)
    await callback.message.edit_text(
        "🔍 <b>Поиск материалов</b>\n\n"
        "Напиши название (или часть названия) материала.\n\n"
        "Например: <i>python</i>, <i>SQL</i>, <i>цикл</i>.",
        reply_markup=back_to_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(F.text & ~F.text.startswith("/"))
async def handle_search_input(message: Message):
    user_id = message.from_user.id
    if user_id not in search_waiting:
        return

    search_waiting.discard(user_id)
    query = message.text.strip()

    if len(query) < 2:
        await message.answer("Слишком короткий запрос. Введи хотя бы 2 символа.")
        return

    results = search_materials(query)

    if not results:
        await message.answer(
            f"❌ По запросу «{query}» ничего не найдено.\n\n"
            "Попробуй другое слово или открой 📚 Учебные материалы.",
            reply_markup=back_to_menu_kb()
        )
        return

    await message.answer(
        f"🔍 Найдено материалов: <b>{len(results)}</b>\n\nВыбери материал:",
        reply_markup=search_results_kb(results),
        parse_mode="HTML"
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