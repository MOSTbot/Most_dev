from aiogram.dispatcher.filters.state import StatesGroup, State


class FSMFeedback(StatesGroup):
    feedback = State()
    send_feedback = State()


class FSMAddAdmin(StatesGroup):
    add_admin_id = State()
    add_admin_name = State()
    confirm = State()


class FSMDeleteAdmin(StatesGroup):
    delete_admin_id = State()
    confirm = State()


class FSMAddAssertion(StatesGroup):
    initialize = State()
    add_assertion = State()
    facts_init = State()
    add_facts = State()
    confirm = State()
