from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.kb import InlineMarkups, ReplyMarkups
from tgbot.utils import SQLRequests
from tgbot.utils.util_classes import SectionName


def register_main_menu_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(start, commands=["start"], state="*")
    dp.register_message_handler(main_menu, commands=["menu"], state="*")
    dp.register_message_handler(main_menu, Text(contains='Главное меню', ignore_case=True), state="*")
    dp.register_message_handler(data_privacy, commands=["privacy"], state="*")
    dp.register_callback_query_handler(data_privacy, text='data_privacy', state="*")
    dp.register_message_handler(data_privacy_answers, lambda message: message.text in SQLRequests
                                .select_by_table_and_column('data_privacy', 'dp_question'),
                                state="*")


async def start(message: Message) -> None:
    SectionName.s_name = 'Стартовое меню'  # for logging purposes
    await message.answer_photo(photo=open('tgbot/assets/start.jpg', 'rb'),
                               caption='<b>Мы ответственны за тех, кого приручила пропаганда</b>.\n'
                                       'Особенно за родных, любимых и друзей.\n\n'
                                       'Разве не достаточно просто сказать правду?\n'
                                       'Увы, многие сталкивались с тем, что '
                                       '<b>правду не слышат или не хотят слышать</b>. Но это не повод сдаваться.\n\n'
                                       'МОСТ — cовместный проект <a href="https://relocation.guide/">гайда в свободный мир</a> и XZ foundation. '
                                       'Это сценарии разговоров с близкими о войне.\n\n'
                                       'Их разработали волонтеры гайда <b>с опытом переубеждения</b> близких, а '
                                       '<b>психологи, социологи и журналисты</b> добавили научную базу.\n\n'
                                       'Разговор о войне не будет простым и быстрым.\n\n'
                                       'Мы верим, что <b>экспертный подход, общественный вклад и эмпатия</b> помогут «вернуть связь» '
                                       'с близкими и создать продукт, который основан на способности слышать, '
                                       'мыслить и противостоять ложным мнениям.',
                               reply_markup=InlineMarkups.create_im(1, ['Перейти в главное меню',
                                                                        'Политика конфиденциальности'],
                                                                    ['main_menu', 'data_privacy']))


async def main_menu(message: Message, state: FSMContext) -> None:
    SectionName.s_name = 'Главное меню'  # for logging purposes
    await state.update_data(flag=False)
    await message.answer_photo(
        photo=open('tgbot/assets/menu.jpg', 'rb'),
        caption='Какое направление вы хотите запустить?',
        reply_markup=ReplyMarkups.create_rm(2, True, *SQLRequests
                                            .select_by_table_and_column('main_menu', 'main_menu_name')))
    await message.answer(SQLRequests.select_main_menu_description(),
                         reply_markup=InlineMarkups.create_im(2, ['Узнать больше о проекте'], ['sc'], [
                             'https://relocation.guide/most']))  # FIXME: The link needs to be replaced


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
