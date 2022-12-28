from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.handlers import main_menu
from tgbot.kb import ReplyMarkups
from tgbot.utils import SQLRequests


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(search, state=None)
    dp.register_callback_query_handler(cb_home, text='main_menu', state=None)


async def cb_home(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    await state.finish()
    await main_menu(call.message, state)


async def search(message: Message) -> None:
    assertions = SQLRequests.select_by_table_and_column('assertions', 'assertion_name')
    a_assertions = SQLRequests.select_by_table_and_column('a_assertions', 'a_assertion_name')
    assertions.extend(a_assertions)
    res: list[str] = []
    msg = " ".join(message.text.split())  # Remove extra spaces
    for count, v in enumerate(map(str.lower, assertions)):
        if msg.lower() in v and len(res) < 6:  # Can be more complicated
            res.append(assertions[count])
    if res:
        await message.answer('Возможно вы имели в виду это? ⬇',
                             reply_markup=ReplyMarkups.create_rm(2, True, *res))
    else:
        await  message.answer(
            'Извините, я не смог распознать вопрос. Попробуйте еще раз или воспользуйтесь меню ниже ⬇',
            reply_markup=ReplyMarkups
            .create_rm(2, True, *SQLRequests.select_by_table_and_column('main_menu', 'main_menu_name')))
