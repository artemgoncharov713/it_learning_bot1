from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# ============================================================
# ОСНОВНЫЕ
# ============================================================

def main_menu_kb(is_admin: bool = False) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Учебные материалы", callback_data="menu_materials")
    builder.button(text="🔍 Поиск материалов", callback_data="menu_search")
    builder.button(text="⭐ Избранное", callback_data="menu_favorites")
    builder.button(text="ℹ️ О боте", callback_data="menu_about")
    if is_admin:
        builder.button(text="👨‍🏫 Админ-панель", callback_data="admin_menu")
        builder.adjust(2, 2, 1)
    else:
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


def search_results_kb(materials) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in materials:
        builder.button(text=m["name"], callback_data=f"material:{m['id']}")
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def favorites_kb(materials) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for m in materials:
        builder.button(text=m["name"], callback_data=f"fav_view:{m['id']}")
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def fav_material_card_kb(material_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="❌ Удалить из избранного",
        callback_data=f"fav_del:{material_id}"
    )
    builder.button(text="⬅️ К избранному", callback_data="menu_favorites")
    builder.adjust(1)
    return builder.as_markup()


# ============================================================
# АДМИНКА
# ============================================================

def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Дисциплины", callback_data="admin_subjects")
    builder.button(text="📖 Темы", callback_data="admin_topics")
    builder.button(text="📄 Материалы", callback_data="admin_materials")
    builder.button(text="⬅️ В главное меню", callback_data="back_to_menu")
    builder.adjust(2, 2)
    return builder.as_markup()


def admin_subjects_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить", callback_data="admin_add_subject")
    builder.button(text="✏️ Изменить", callback_data="admin_edit_subject")
    builder.button(text="❌ Удалить", callback_data="admin_del_subject")
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_topics_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить", callback_data="admin_add_topic")
    builder.button(text="✏️ Изменить", callback_data="admin_edit_topic")
    builder.button(text="❌ Удалить", callback_data="admin_del_topic")
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_materials_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить", callback_data="admin_add_material")
    builder.button(text="✏️ Изменить", callback_data="admin_edit_material")
    builder.button(text="❌ Удалить", callback_data="admin_del_material")
    builder.button(text="⬅️ Назад", callback_data="admin_menu")
    builder.adjust(1)
    return builder.as_markup()


def admin_list_kb(items, prefix: str, back_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for item in items:
        builder.button(
            text=item["name"],
            callback_data=f"{prefix}:{item['id']}"
        )
    builder.button(text="⬅️ Назад", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def cancel_kb(back_callback: str = "admin_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data=back_callback)
    return builder.as_markup()


def skip_or_cancel_kb(back_callback: str = "admin_menu") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⏭ Пропустить", callback_data="admin_skip")
    builder.button(text="❌ Отмена", callback_data=back_callback)
    builder.adjust(2)
    return builder.as_markup()


def confirm_delete_kb(prefix: str, item_id: int,
                      back_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🗑 Да, удалить", callback_data=f"{prefix}:{item_id}")
    builder.button(text="❌ Отмена", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def material_types_kb(back_callback: str = "admin_materials") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📖 теория", callback_data="mtype:теория")
    builder.button(text="💻 примеры кода", callback_data="mtype:примеры кода")
    builder.button(text="📝 практические задания",
                   callback_data="mtype:практические задания")
    builder.button(text="📎 дополнительный материал",
                   callback_data="mtype:дополнительный материал")
    builder.button(text="❌ Отмена", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def edit_material_fields_kb(material_id: int,
                            back_callback: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="📝 Название",
                   callback_data=f"edit_m_field:name:{material_id}")
    builder.button(text="🏷 Тип",
                   callback_data=f"edit_m_field:material_type:{material_id}")
    builder.button(text="🔗 Ссылка",
                   callback_data=f"edit_m_field:link:{material_id}")
    builder.button(text="📄 Описание",
                   callback_data=f"edit_m_field:description:{material_id}")
    builder.button(text="📺 Видео-ссылка",
                   callback_data=f"edit_m_field:video_link:{material_id}")
    builder.button(text="📎 Файл",
                   callback_data=f"edit_m_field:file_id:{material_id}")
    builder.button(text="⬅️ Назад", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()