from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def main_menu_kb() -> InlineKeyboardMarkup:
    """Главное меню бота."""
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Учебные материалы", callback_data="menu_materials")
    builder.button(text="🔍 Поиск материалов", callback_data="menu_search")
    builder.button(text="⭐ Избранное", callback_data="menu_favorites")
    builder.button(text="ℹ️ О боте", callback_data="menu_about")
    builder.adjust(2, 2)  # 2 кнопки в первом ряду, 2 во втором
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню."""
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    return builder.as_markup()

