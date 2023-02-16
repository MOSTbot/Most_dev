from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMFeedback(StatesGroup):
    feedback = State()
    send_feedback = State()
    send_private_contacts = State()


class FSMAddAdmin(StatesGroup):
    add_admin_id = State()
    add_admin_name = State()
    confirm = State()


class FSMDeleteAdmin(StatesGroup):
    delete_admin_id = State()
    confirm = State()
