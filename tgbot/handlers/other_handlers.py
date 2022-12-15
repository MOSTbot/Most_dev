from __future__ import annotations

from logging import info

from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

from tgbot.handlers import menu_handler
from tgbot.kb import ReplyMarkups
from tgbot.utils import SQLRequests


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(text_wasnt_found, state=None)
    dp.register_callback_query_handler(cb_home, text='main_menu', state=None)


def user_log(user_id: str | int, message_text: str) -> None:
    return info(f'{user_id=} {message_text=}')


async def cb_home(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    await menu_handler(call.message)


async def text_wasnt_found(message: Message) -> None:
    await  message.answer(
        'Извините, я не смог распознать вопрос. Попробуйте еще раз или воспользуйтесь меню ниже ⬇',
        reply_markup=ReplyMarkups
        .create_rm(2, True, *SQLRequests.select_by_table_and_column('main_menu', 'main_menu_name')))
