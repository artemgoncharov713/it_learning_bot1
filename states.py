from aiogram.fsm.state import State, StatesGroup


class AddSubject(StatesGroup):
    name = State()


class EditSubject(StatesGroup):
    choose = State()
    name = State()


class DeleteSubject(StatesGroup):
    choose = State()
    confirm = State()


class AddTopic(StatesGroup):
    subject = State()
    name = State()


class EditTopic(StatesGroup):
    subject = State()
    choose = State()
    name = State()


class DeleteTopic(StatesGroup):
    subject = State()
    choose = State()
    confirm = State()


class AddMaterial(StatesGroup):
    subject = State()
    topic = State()
    name = State()
    mtype = State()
    link = State()
    description = State()
    video_link = State()
    file = State()


class EditMaterial(StatesGroup):
    subject = State()
    topic = State()
    choose = State()
    field = State()
    value = State()


class DeleteMaterial(StatesGroup):
    subject = State()
    topic = State()
    choose = State()
    confirm = State()