from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.handlers.section_descriptions import main_menu_handlers
from tgbot.kb import InlineMarkups, ReplyMarkups
from tgbot.misc import SQLRequests, SQLInserts
from tgbot.misc.utils import SectionName


def register_main_menu_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(main_menu, commands=["menu"], state="*")
    dp.register_message_handler(main_menu, Text(contains='Главное меню', ignore_case=True), state="*")


async def start(message: Message) -> None:
    SectionName.s_name = 'Стартовое меню'  # for logging purposes
    tid, username = int(message.from_user.id), message.from_user.username
    full_name = message.from_user.full_name
    await SQLInserts.newcomers(tid=tid, username=username, full_name=full_name)
    await message.answer_photo(photo=open('tgbot/assets/start.jpg', 'rb'),
                               caption=main_menu_handlers['start']['caption'],
                               reply_markup=InlineMarkups.create_im(1, ['Перейти в главное меню'],
                                                                    ['main_menu']))


async def main_menu(message: Message, state: FSMContext) -> None:
    SectionName.s_name = 'Главное меню'  # for logging purposes
    await state.update_data(flag=False)
    await message.answer_photo(
        photo=open('tgbot/assets/menu.jpg', 'rb'),
        caption='Какое направление вы хотите запустить?',
        reply_markup=ReplyMarkups.create_rm(2, True, *SQLRequests
                                            .select_by_table_and_column('main_menu', 'main_menu_name')))
    await message.answer(SQLRequests
                         .select_main_menu_description(), reply_markup=InlineMarkups
                         .create_im(1, ['Узнать больше о проекте'], ['sc'],
                                    ['https://relocation.guide/most', '']))  # FIXME: The link needs to be replaced
    if res := SQLRequests.select_by_table_and_column('notifications', 'notification'):
        await message.answer(res[0])


async def data_privacy(call: CallbackQuery | Message) -> None:
    if isinstance(call, Message):
        call.message = call
    elif isinstance(call, CallbackQuery):
        await call.answer(cache_time=5)
    await call.message.answer('Выберите вопрос ⬇', reply_markup=ReplyMarkups
                              .create_rm(2, False,
                                         *SQLRequests.select_by_table_and_column('data_privacy', 'dp_question')))


async def data_privacy_answers(message: Message) -> None:
    await message.answer(
        *SQLRequests.select_by_table_and_column('data_privacy', 'dp_answer', 'dp_question', message.text),
        reply_markup=InlineMarkups.create_im(1, ['Перейти в главное меню'], ['main_menu']))
