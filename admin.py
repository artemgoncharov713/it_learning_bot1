from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config import ADMIN_IDS
from database import (
    get_subjects, get_topics, get_materials,
    add_subject, update_subject, delete_subject,
    add_topic, update_topic, delete_topic,
    add_material, update_material, delete_material,
)
from keyboards import (
    admin_menu_kb, admin_subjects_kb, admin_topics_kb,
    admin_materials_kb, admin_list_kb, cancel_kb,
    skip_or_cancel_kb, confirm_delete_kb,
    material_types_kb, edit_material_fields_kb,
)
from states import (
    AddSubject, EditSubject, DeleteSubject,
    AddTopic, EditTopic, DeleteTopic,
    AddMaterial, EditMaterial, DeleteMaterial,
)


router = Router()


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# ============================================================
# ГЛАВНОЕ МЕНЮ АДМИНКИ
# ============================================================

@router.callback_query(F.data == "admin_menu")
async def admin_menu(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        await callback.answer("Доступ запрещён", show_alert=True)
        return
    await state.clear()
    await callback.message.edit_text(
        "👨‍🏫 <b>Админ-панель</b>\n\nВыбери раздел:",
        reply_markup=admin_menu_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_subjects")
async def admin_subjects(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "📚 <b>Дисциплины</b>\n\nВыбери действие:",
        reply_markup=admin_subjects_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_topics")
async def admin_topics(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "📖 <b>Темы</b>\n\nВыбери действие:",
        reply_markup=admin_topics_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_materials")
async def admin_materials(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.clear()
    await callback.message.edit_text(
        "📄 <b>Материалы</b>\n\nВыбери действие:",
        reply_markup=admin_materials_kb(),
        parse_mode="HTML"
    )
    await callback.answer()


# ============================================================
# ДИСЦИПЛИНЫ
# ============================================================

@router.callback_query(F.data == "admin_add_subject")
async def add_subject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    await state.set_state(AddSubject.name)
    await callback.message.edit_text(
        "📚 Введи название новой дисциплины:",
        reply_markup=cancel_kb("admin_subjects")
    )
    await callback.answer()


@router.message(AddSubject.name)
async def add_subject_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Слишком короткое название.")
        return
    add_subject(name)
    await state.clear()
    await message.answer(
        f"✅ Дисциплина «{name}» добавлена.",
        reply_markup=admin_subjects_kb()
    )


@router.callback_query(F.data == "admin_edit_subject")
async def edit_subject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(EditSubject.choose)
    await callback.message.edit_text(
        "Выбери дисциплину для изменения:",
        reply_markup=admin_list_kb(subjects, "edit_subject_sel", "admin_subjects")
    )
    await callback.answer()


@router.callback_query(EditSubject.choose, F.data.startswith("edit_subject_sel:"))
async def edit_subject_choose(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    await state.update_data(subject_id=subject_id)
    await state.set_state(EditSubject.name)
    await callback.message.edit_text(
        "Введи новое название дисциплины:",
        reply_markup=cancel_kb("admin_subjects")
    )
    await callback.answer()


@router.message(EditSubject.name)
async def edit_subject_name(message: Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    update_subject(data["subject_id"], name)
    await state.clear()
    await message.answer(
        f"✅ Дисциплина переименована в «{name}».",
        reply_markup=admin_subjects_kb()
    )


@router.callback_query(F.data == "admin_del_subject")
async def del_subject_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(DeleteSubject.choose)
    await callback.message.edit_text(
        "Выбери дисциплину для удаления:",
        reply_markup=admin_list_kb(subjects, "del_subject_sel", "admin_subjects")
    )
    await callback.answer()


@router.callback_query(DeleteSubject.choose, F.data.startswith("del_subject_sel:"))
async def del_subject_choose(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    await state.update_data(subject_id=subject_id)
    await state.set_state(DeleteSubject.confirm)
    await callback.message.edit_text(
        "⚠️ Удалить дисциплину?\n\nПодтверди:",
        reply_markup=confirm_delete_kb("del_subject_ok", subject_id, "admin_subjects")
    )
    await callback.answer()


@router.callback_query(DeleteSubject.confirm, F.data.startswith("del_subject_ok:"))
async def del_subject_confirm(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    delete_subject(subject_id)
    await state.clear()
    await callback.message.edit_text(
        "✅ Дисциплина удалена.",
        reply_markup=admin_subjects_kb()
    )
    await callback.answer()


# ============================================================
# ТЕМЫ
# ============================================================

@router.callback_query(F.data == "admin_add_topic")
async def add_topic_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(AddTopic.subject)
    await callback.message.edit_text(
        "Выбери дисциплину для новой темы:",
        reply_markup=admin_list_kb(subjects, "add_topic_subj", "admin_topics")
    )
    await callback.answer()


@router.callback_query(AddTopic.subject, F.data.startswith("add_topic_subj:"))
async def add_topic_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    await state.update_data(subject_id=subject_id)
    await state.set_state(AddTopic.name)
    await callback.message.edit_text(
        "Введи название новой темы:",
        reply_markup=cancel_kb("admin_topics")
    )
    await callback.answer()


@router.message(AddTopic.name)
async def add_topic_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Слишком короткое название.")
        return
    data = await state.get_data()
    add_topic(data["subject_id"], name)
    await state.clear()
    await message.answer(
        f"✅ Тема «{name}» добавлена.",
        reply_markup=admin_topics_kb()
    )


@router.callback_query(F.data == "admin_edit_topic")
async def edit_topic_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(EditTopic.subject)
    await callback.message.edit_text(
        "Выбери дисциплину:",
        reply_markup=admin_list_kb(subjects, "edit_topic_subj", "admin_topics")
    )
    await callback.answer()


@router.callback_query(EditTopic.subject, F.data.startswith("edit_topic_subj:"))
async def edit_topic_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.answer("Нет тем", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await state.set_state(EditTopic.choose)
    await callback.message.edit_text(
        "Выбери тему для изменения:",
        reply_markup=admin_list_kb(topics, "edit_topic_sel", "admin_topics")
    )
    await callback.answer()


@router.callback_query(EditTopic.choose, F.data.startswith("edit_topic_sel:"))
async def edit_topic_choose(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    await state.update_data(topic_id=topic_id)
    await state.set_state(EditTopic.name)
    await callback.message.edit_text(
        "Введи новое название темы:",
        reply_markup=cancel_kb("admin_topics")
    )
    await callback.answer()


@router.message(EditTopic.name)
async def edit_topic_name(message: Message, state: FSMContext):
    name = message.text.strip()
    data = await state.get_data()
    update_topic(data["topic_id"], name)
    await state.clear()
    await message.answer(
        f"✅ Тема переименована в «{name}».",
        reply_markup=admin_topics_kb()
    )


@router.callback_query(F.data == "admin_del_topic")
async def del_topic_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(DeleteTopic.subject)
    await callback.message.edit_text(
        "Выбери дисциплину:",
        reply_markup=admin_list_kb(subjects, "del_topic_subj", "admin_topics")
    )
    await callback.answer()


@router.callback_query(DeleteTopic.subject, F.data.startswith("del_topic_subj:"))
async def del_topic_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.answer("Нет тем", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await state.set_state(DeleteTopic.choose)
    await callback.message.edit_text(
        "Выбери тему для удаления:",
        reply_markup=admin_list_kb(topics, "del_topic_sel", "admin_topics")
    )
    await callback.answer()


@router.callback_query(DeleteTopic.choose, F.data.startswith("del_topic_sel:"))
async def del_topic_choose(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    await state.update_data(topic_id=topic_id)
    await state.set_state(DeleteTopic.confirm)
    await callback.message.edit_text(
        "⚠️ Удалить тему?\n\nПодтверди:",
        reply_markup=confirm_delete_kb("del_topic_ok", topic_id, "admin_topics")
    )
    await callback.answer()


@router.callback_query(DeleteTopic.confirm, F.data.startswith("del_topic_ok:"))
async def del_topic_confirm(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    delete_topic(topic_id)
    await state.clear()
    await callback.message.edit_text(
        "✅ Тема удалена.",
        reply_markup=admin_topics_kb()
    )
    await callback.answer()


# ============================================================
# МАТЕРИАЛЫ — ДОБАВЛЕНИЕ (8 шагов)
# ============================================================

@router.callback_query(F.data == "admin_add_material")
async def add_material_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(AddMaterial.subject)
    await callback.message.edit_text(
        "Шаг 1/8. Выбери дисциплину:",
        reply_markup=admin_list_kb(subjects, "add_mat_subj", "admin_materials")
    )
    await callback.answer()


@router.callback_query(AddMaterial.subject, F.data.startswith("add_mat_subj:"))
async def add_mat_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.answer("Нет тем в этой дисциплине", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await state.set_state(AddMaterial.topic)
    await callback.message.edit_text(
        "Шаг 2/8. Выбери тему:",
        reply_markup=admin_list_kb(topics, "add_mat_topic", "admin_materials")
    )
    await callback.answer()


@router.callback_query(AddMaterial.topic, F.data.startswith("add_mat_topic:"))
async def add_mat_topic(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    await state.update_data(topic_id=topic_id)
    await state.set_state(AddMaterial.name)
    await callback.message.edit_text(
        "Шаг 3/8. Введи название материала:",
        reply_markup=cancel_kb("admin_materials")
    )
    await callback.answer()


@router.message(AddMaterial.name)
async def add_mat_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if len(name) < 2:
        await message.answer("Слишком короткое название.")
        return
    await state.update_data(name=name)
    await state.set_state(AddMaterial.mtype)
    await message.answer(
        "Шаг 4/8. Выбери тип:",
        reply_markup=material_types_kb("admin_materials")
    )


@router.callback_query(AddMaterial.mtype, F.data.startswith("mtype:"))
async def add_mat_mtype(callback: CallbackQuery, state: FSMContext):
    mtype = callback.data.split(":", 1)[1]
    await state.update_data(mtype=mtype)
    await state.set_state(AddMaterial.link)
    await callback.message.edit_text(
        "Шаг 5/8. Введи ссылку на материал:",
        reply_markup=cancel_kb("admin_materials")
    )
    await callback.answer()


@router.message(AddMaterial.link)
async def add_mat_link(message: Message, state: FSMContext):
    link = message.text.strip()
    if not (link.startswith("http://") or link.startswith("https://")):
        await message.answer("Ссылка должна начинаться с http:// или https://")
        return
    await state.update_data(link=link)
    await state.set_state(AddMaterial.description)
    await message.answer(
        "Шаг 6/8. Введи описание (или «Пропустить»):",
        reply_markup=skip_or_cancel_kb("admin_materials")
    )


@router.callback_query(AddMaterial.description, F.data == "admin_skip")
async def add_mat_desc_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(description=None)
    await state.set_state(AddMaterial.video_link)
    await callback.message.edit_text(
        "Шаг 7/8. Ссылка на видеоурок (или «Пропустить»):",
        reply_markup=skip_or_cancel_kb("admin_materials")
    )
    await callback.answer()


@router.message(AddMaterial.description)
async def add_mat_desc(message: Message, state: FSMContext):
    await state.update_data(description=message.text.strip())
    await state.set_state(AddMaterial.video_link)
    await message.answer(
        "Шаг 7/8. Ссылка на видеоурок (или «Пропустить»):",
        reply_markup=skip_or_cancel_kb("admin_materials")
    )


@router.callback_query(AddMaterial.video_link, F.data == "admin_skip")
async def add_mat_video_skip(callback: CallbackQuery, state: FSMContext):
    await state.update_data(video_link=None)
    await state.set_state(AddMaterial.file)
    await callback.message.edit_text(
        "Шаг 8/8. Прикрепи файл или «Пропустить»:",
        reply_markup=skip_or_cancel_kb("admin_materials")
    )
    await callback.answer()


@router.message(AddMaterial.video_link)
async def add_mat_video(message: Message, state: FSMContext):
    await state.update_data(video_link=message.text.strip())
    await state.set_state(AddMaterial.file)
    await message.answer(
        "Шаг 8/8. Прикрепи файл или «Пропустить»:",
        reply_markup=skip_or_cancel_kb("admin_materials")
    )


@router.message(AddMaterial.file, F.document)
async def add_mat_file(message: Message, state: FSMContext):
    data = await state.get_data()
    add_material(
        topic_id=data["topic_id"],
        name=data["name"],
        material_type=data["mtype"],
        link=data["link"],
        description=data.get("description"),
        video_link=data.get("video_link"),
        file_id=message.document.file_id,
    )
    await state.clear()
    await message.answer(
        f"✅ Материал «{data['name']}» добавлен с файлом.",
        reply_markup=admin_materials_kb()
    )


@router.callback_query(AddMaterial.file, F.data == "admin_skip")
async def add_mat_file_skip(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    add_material(
        topic_id=data["topic_id"],
        name=data["name"],
        material_type=data["mtype"],
        link=data["link"],
        description=data.get("description"),
        video_link=data.get("video_link"),
        file_id=None,
    )
    await state.clear()
    await callback.message.edit_text(
        f"✅ Материал «{data['name']}» добавлен.",
        reply_markup=admin_materials_kb()
    )
    await callback.answer()


# ============================================================
# МАТЕРИАЛЫ — ИЗМЕНЕНИЕ
# ============================================================

@router.callback_query(F.data == "admin_edit_material")
async def edit_material_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(EditMaterial.subject)
    await callback.message.edit_text(
        "Выбери дисциплину:",
        reply_markup=admin_list_kb(subjects, "edit_mat_subj", "admin_materials")
    )
    await callback.answer()


@router.callback_query(EditMaterial.subject, F.data.startswith("edit_mat_subj:"))
async def edit_mat_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.answer("Нет тем", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await state.set_state(EditMaterial.topic)
    await callback.message.edit_text(
        "Выбери тему:",
        reply_markup=admin_list_kb(topics, "edit_mat_topic", "admin_materials")
    )
    await callback.answer()


@router.callback_query(EditMaterial.topic, F.data.startswith("edit_mat_topic:"))
async def edit_mat_topic(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    materials = get_materials(topic_id)
    if not materials:
        await callback.answer("Нет материалов", show_alert=True)
        return
    await state.update_data(topic_id=topic_id)
    await state.set_state(EditMaterial.choose)
    await callback.message.edit_text(
        "Выбери материал:",
        reply_markup=admin_list_kb(materials, "edit_mat_sel", "admin_materials")
    )
    await callback.answer()


@router.callback_query(EditMaterial.choose, F.data.startswith("edit_mat_sel:"))
async def edit_mat_choose(callback: CallbackQuery, state: FSMContext):
    material_id = int(callback.data.split(":")[1])
    await state.update_data(material_id=material_id)
    await state.set_state(EditMaterial.field)
    await callback.message.edit_text(
        "Что изменить?",
        reply_markup=edit_material_fields_kb(material_id, "admin_materials")
    )
    await callback.answer()


@router.callback_query(EditMaterial.field, F.data.startswith("edit_m_field:"))
async def edit_mat_field(callback: CallbackQuery, state: FSMContext):
    parts = callback.data.split(":")
    field = parts[1]
    material_id = int(parts[2])
    await state.update_data(field=field, material_id=material_id)

    if field == "material_type":
        await callback.message.edit_text(
            "Выбери новый тип:",
            reply_markup=material_types_kb("admin_materials")
        )
        await callback.answer()
        return

    if field == "file_id":
        await state.set_state(EditMaterial.value)
        await callback.message.edit_text(
            "Отправь новый файл:",
            reply_markup=cancel_kb("admin_materials")
        )
        await callback.answer()
        return

    await state.set_state(EditMaterial.value)
    await callback.message.edit_text(
        f"Введи новое значение для «{field}»:",
        reply_markup=cancel_kb("admin_materials")
    )
    await callback.answer()


@router.callback_query(EditMaterial.field, F.data.startswith("mtype:"))
async def edit_mat_mtype(callback: CallbackQuery, state: FSMContext):
    mtype = callback.data.split(":", 1)[1]
    data = await state.get_data()
    update_material(data["material_id"], "material_type", mtype)
    await state.clear()
    await callback.message.edit_text(
        f"✅ Тип обновлён на «{mtype}».",
        reply_markup=admin_materials_kb()
    )
    await callback.answer()


@router.message(EditMaterial.value, F.document)
async def edit_mat_value_file(message: Message, state: FSMContext):
    data = await state.get_data()
    update_material(data["material_id"], "file_id", message.document.file_id)
    await state.clear()
    await message.answer(
        "✅ Файл обновлён.",
        reply_markup=admin_materials_kb()
    )


@router.message(EditMaterial.value)
async def edit_mat_value(message: Message, state: FSMContext):
    data = await state.get_data()
    update_material(data["material_id"], data["field"], message.text.strip())
    await state.clear()
    await message.answer(
        f"✅ Поле «{data['field']}» обновлено.",
        reply_markup=admin_materials_kb()
    )


# ============================================================
# МАТЕРИАЛЫ — УДАЛЕНИЕ
# ============================================================

@router.callback_query(F.data == "admin_del_material")
async def del_material_start(callback: CallbackQuery, state: FSMContext):
    if not is_admin(callback.from_user.id):
        return
    subjects = get_subjects()
    if not subjects:
        await callback.answer("Нет дисциплин", show_alert=True)
        return
    await state.set_state(DeleteMaterial.subject)
    await callback.message.edit_text(
        "Выбери дисциплину:",
        reply_markup=admin_list_kb(subjects, "del_mat_subj", "admin_materials")
    )
    await callback.answer()


@router.callback_query(DeleteMaterial.subject, F.data.startswith("del_mat_subj:"))
async def del_mat_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split(":")[1])
    topics = get_topics(subject_id)
    if not topics:
        await callback.answer("Нет тем", show_alert=True)
        return
    await state.update_data(subject_id=subject_id)
    await state.set_state(DeleteMaterial.topic)
    await callback.message.edit_text(
        "Выбери тему:",
        reply_markup=admin_list_kb(topics, "del_mat_topic", "admin_materials")
    )
    await callback.answer()


@router.callback_query(DeleteMaterial.topic, F.data.startswith("del_mat_topic:"))
async def del_mat_topic(callback: CallbackQuery, state: FSMContext):
    topic_id = int(callback.data.split(":")[1])
    materials = get_materials(topic_id)
    if not materials:
        await callback.answer("Нет материалов", show_alert=True)
        return
    await state.update_data(topic_id=topic_id)
    await state.set_state(DeleteMaterial.choose)
    await callback.message.edit_text(
        "Выбери материал:",
        reply_markup=admin_list_kb(materials, "del_mat_sel", "admin_materials")
    )
    await callback.answer()


@router.callback_query(DeleteMaterial.choose, F.data.startswith("del_mat_sel:"))
async def del_mat_choose(callback: CallbackQuery, state: FSMContext):
    material_id = int(callback.data.split(":")[1])
    await state.update_data(material_id=material_id)
    await state.set_state(DeleteMaterial.confirm)
    await callback.message.edit_text(
        "⚠️ Удалить материал?\n\nПодтверди:",
        reply_markup=confirm_delete_kb("del_mat_ok", material_id, "admin_materials")
    )
    await callback.answer()


@router.callback_query(DeleteMaterial.confirm, F.data.startswith("del_mat_ok:"))
async def del_mat_confirm(callback: CallbackQuery, state: FSMContext):
    material_id = int(callback.data.split(":")[1])
    delete_material(material_id)
    await state.clear()
    await callback.message.edit_text(
        "✅ Материал удалён.",
        reply_markup=admin_materials_kb()
    )
    await callback.answer()