from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.handlers import main_menu
from tgbot.kb import ReplyMarkups
from tgbot.utils import SQLRequests, SearchIndex


def register_other_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(search, state=None)
    dp.register_message_handler(other_content_types, content_types=
    ['photo', 'document', 'sticker', 'audio', 'animation'], state="*")
    dp.register_callback_query_handler(cb_home, text='main_menu', state=None)


async def cb_home(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await main_menu(call.message, state)


async def other_content_types(message: Message):
    await message.answer('Я могу обрабатывать только текстовые сообщения 🤖')


async def search(message: Message) -> None:
    res: list[str] = []
    msg = " ".join(message.text.split())  # Remove extra spaces
    for count, v in enumerate(map(str.lower, SearchIndex.search_index)):
        if msg.lower() in v and len(res) < 6:  # Can be more complicated
            res.append(SearchIndex.search_index[count])
    if res:
        await message.answer('Возможно вы имели в виду это? ⬇',
                             reply_markup=ReplyMarkups.create_rm(2, True, *res))
    else:
        await  message.answer(
            'Извините, я не смог распознать вопрос. Попробуйте еще раз или воспользуйтесь меню ниже ⬇',
            reply_markup=ReplyMarkups
            .create_rm(2, True, *SQLRequests.select_by_table_and_column('main_menu', 'main_menu_name')))
