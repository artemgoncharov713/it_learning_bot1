from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from config import ADMIN_IDS
from database import (
    get_subjects,
    get_subject,
    add_subject,
    update_subject,
    delete_subject,
)
from keyboards import (
    admin_menu_kb,
    admin_subjects_kb,
    admin_list_kb,
    cancel_kb,
    confirm_delete_kb,
)
from states import (
    AddSubject,
    EditSubject,
    DeleteSubject,
)


admin_router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ============================================================
# ГЛАВНОЕ МЕНЮ АДМИНКИ
# ============================================================

@admin_router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.message.edit_text(
        "👨‍🏫 <b>Админ-панель</b>\n\nВыбери раздел:",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


# ============================================================
# РАЗДЕЛ «ДИСЦИПЛИНЫ»
# ============================================================

@admin_router.callback_query(F.data == "admin_subjects")
async def admin_subjects(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await state.clear()
    await callback.message.edit_text(
        "📚 <b>Дисциплины</b>\n\nВыбери действие:",
        reply_markup=admin_subjects_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


# ============================================================
# ДОБАВИТЬ ДИСЦИПЛИНУ
# ============================================================

@admin_router.callback_query(F.data == "admin_add_subject")
async def add_subject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    await callback.message.edit_text(
        "📚 <b>Добавление дисциплины</b>\n\n"
        "Напиши название новой дисциплины.\n\n"
        "Например: <i>Основы Python</i>",
        reply_markup=cancel_kb("admin_subjects"),
        parse_mode="HTML"
    )
    await state.set_state(AddSubject.name)
    await callback.answer()


@admin_router.message(AddSubject.name)
async def add_subject_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    name = message.text.strip()
    if len(name) < 2:
        await message.answer(
            "Слишком короткое название. Введи хотя бы 2 символа.",
            reply_markup=cancel_kb("admin_subjects")
        )
        return

    subject_id = add_subject(name)
    await state.clear()

    await message.answer(
        f"✅ Дисциплина «{name}» добавлена (id={subject_id}).",
        reply_markup=admin_subjects_kb()
    )


# ============================================================
# ИЗМЕНИТЬ ДИСЦИПЛИНУ
# ============================================================

@admin_router.callback_query(F.data == "admin_edit_subject")
async def edit_subject_choose(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    subjects = get_subjects()
    if not subjects:
        await callback.message.edit_text(
            "📚 Пока нет ни одной дисциплины.",
            reply_markup=admin_subjects_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "✏️ <b>Какую дисциплину изменить?</b>",
        reply_markup=admin_list_kb(
            subjects,
            prefix="admin_edit_subject_sel",
            back_callback="admin_subjects"
        ),
        parse_mode="HTML"
    )
    await state.set_state(EditSubject.choose)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin_edit_subject_sel:"))
async def edit_subject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    subject_id = int(callback.data.split(":")[1])
    subject = get_subject(subject_id)
    if not subject:
        await callback.answer("Не найдено", show_alert=True)
        return

    await state.update_data(subject_id=subject_id)

    await callback.message.edit_text(
        f"✏️ <b>Изменение дисциплины</b>\n\n"
        f"Текущее название: <b>{subject['name']}</b>\n\n"
        "Введи новое название:",
        reply_markup=cancel_kb("admin_subjects"),
        parse_mode="HTML"
    )
    await state.set_state(EditSubject.name)
    await callback.answer()


@admin_router.message(EditSubject.name)
async def edit_subject_save(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    name = message.text.strip()
    if len(name) < 2:
        await message.answer(
            "Слишком короткое название. Введи хотя бы 2 символа.",
            reply_markup=cancel_kb("admin_subjects")
        )
        return

    data = await state.get_data()
    subject_id = data.get("subject_id")

    update_subject(subject_id, name)
    await state.clear()

    await message.answer(
        f"✅ Дисциплина переименована в «{name}».",
        reply_markup=admin_subjects_kb()
    )


# ============================================================
# УДАЛИТЬ ДИСЦИПЛИНУ
# ============================================================

@admin_router.callback_query(F.data == "admin_del_subject")
async def del_subject_choose(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    subjects = get_subjects()
    if not subjects:
        await callback.message.edit_text(
            "📚 Пока нет ни одной дисциплины.",
            reply_markup=admin_subjects_kb()
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        "❌ <b>Какую дисциплину удалить?</b>\n\n"
        "⚠️ Вместе с дисциплиной удалятся все её темы и материалы.",
        reply_markup=admin_list_kb(
            subjects,
            prefix="admin_del_subject_sel",
            back_callback="admin_subjects"
        ),
        parse_mode="HTML"
    )
    await state.set_state(DeleteSubject.choose)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin_del_subject_sel:"))
async def del_subject_confirm(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    subject_id = int(callback.data.split(":")[1])
    subject = get_subject(subject_id)
    if not subject:
        await callback.answer("Не найдено", show_alert=True)
        return

    await callback.message.edit_text(
        f"❌ Удалить дисциплину «{subject['name']}»?\n\n"
        "Это действие <b>нельзя отменить</b>.",
        reply_markup=confirm_delete_kb(
            prefix="admin_del_subject_yes",
            item_id=subject_id,
            back_callback="admin_del_subject"
        ),
        parse_mode="HTML"
    )
    await state.set_state(DeleteSubject.confirm)
    await callback.answer()


@admin_router.callback_query(F.data.startswith("admin_del_subject_yes:"))
async def del_subject_do(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Нет доступа", show_alert=True)
        return

    subject_id = int(callback.data.split(":")[1])
    subject = get_subject(subject_id)
    name = subject["name"] if subject else "?"

    delete_subject(subject_id)
    await state.clear()

    await callback.message.edit_text(
        f"✅ Дисциплина «{name}» удалена.",
        reply_markup=admin_subjects_kb()
    )
    await callback.answer()