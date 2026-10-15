from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Учебные материалы", callback_data="menu_materials")
    builder.button(text="🔍 Поиск материалов", callback_data="menu_search")
    builder.button(text="⭐ Избранное", callback_data="menu_favorites")
    builder.button(text="ℹ️ О боте", callback_data="menu_about")
    builder.adjust(2, 2)
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    return builder.as_markup()


def subjects_kb(subjects) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for s in subjects:
        builder.button(text=s["name"], callback_data=f"subject:{s['id']}")
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def topics_kb(topics, subject_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for t in topics:
        builder.button(text=t["name"], callback_data=f"topic:{t['id']}")
    builder.button(text="⬅️ К дисциплинам", callback_data="menu_materials")
    builder.adjust(1)
    return builder.as_markup()


def materials_kb(materials, subject_id: int) -> InlineKeyboardMarkup:
    """Список материалов темы. Назад — к темам этой дисциплины."""
    builder = InlineKeyboardBuilder()
    for m in materials:
        builder.button(text=m["name"], callback_data=f"material:{m['id']}")
    builder.button(text="⬅️ К темам", callback_data=f"subject:{subject_id}")
    builder.adjust(1)
    return builder.as_markup()


def material_card_kb(material_id: int, topic_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⭐ В избранное", callback_data=f"fav_add:{material_id}")
    builder.button(text="⬅️ К материалам", callback_data=f"topic:{topic_id}")
    builder.adjust(1)
    return builder.as_markup()