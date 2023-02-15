from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.kb import ReplyMarkups
from tgbot.utils import FSMFeedback, SQLRequests, SQLInserts, SectionName, HashData

commands_list = ['/start', '/menu', '/chat', '/practice', '/advice', '/theory', '/feedback', '/privacy',
                 '🤓 Оставить отзыв', 'Отмена']


def register_feedback_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(choose_feedback_type, Text(contains='поделиться мнением', ignore_case=True), state=None)
    dp.register_message_handler(choose_feedback_type, commands=['feedback'], state=None)
    dp.register_message_handler(fsm_feedback, Text(equals=['Анонимно', 'Оставить контакт']), state=None)
    dp.register_message_handler(fsm_confirm_feedback, state=FSMFeedback.feedback)
    dp.register_message_handler(fsm_send_feedback, state=FSMFeedback.send_feedback)
    dp.register_callback_query_handler(cb_feedback, text='feedback', state=None)


async def choose_feedback_type(message: Message) -> None:
    SectionName.s_name = 'Оставить отзыв'  # for logging purposes
    await  message.answer(
        'Вы можете отправить нам анонимное сообщение или оставить свои контакты (telegram ID). '
        'Выберите комфортный для вас способ ниже.', reply_markup=ReplyMarkups.create_rm(2, True, 'Анонимно',
                                                                                        'Оставить контакт'))


async def fsm_feedback(message: Message, state: FSMContext) -> None:
    async with state.proxy() as data: data['user_choice'] = message.text
    await  message.answer(
        'Напишите отзыв о нашем проекте или поделитесь своей историей разговора с близкими ⬇',
        reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMFeedback.feedback.set()  # state: feedback


# WARNING: Develop options for completing FSM. Not all state.finish() options have been explored
async def fsm_confirm_feedback(message: Message, state: FSMContext) -> None:
    if message.text in commands_list:
        await message.answer('Написание отзыва отменено пользователем',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
        return await state.finish()
    async with state.proxy() as data: data['user_feedback'] = message.text
    await  message.answer('Оставить отзыв?', reply_markup=ReplyMarkups.create_rm(2, True, 'Оставить отзыв', 'Отмена'))
    await FSMFeedback.next()


async def fsm_send_feedback(message: Message, state: FSMContext) -> None:  # TODO: Checking message for text only type!
    async with state.proxy() as data:
        user_choice = data['user_choice']
        user_feedback = data['user_feedback']
    datetime = str(message.date)
    if message.text == 'Оставить отзыв' and user_choice == 'Анонимно':
        hash_user_id = HashData.hash_data(message.from_user.id)[54:]
        SQLInserts.send_feedback(table='user_feedback', user_id=hash_user_id,
                                 datetime=datetime, feedback=user_feedback)
        await message.answer('Спасибо, ваш отзыв отправлен! 🤗',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
    elif message.text == 'Оставить отзыв' and user_choice == 'Оставить контакт':
        SQLInserts.send_feedback(table='user_feedback_private', user_id=message.from_user.id,
                                 datetime=datetime, feedback=user_feedback)
        await message.delete()
        await message.answer('Ваше сообщение успешно отправлено! ☺', reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
    else:
        await message.answer('Вы отменили отправку отзыва!',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
        await message.delete()
    return await state.finish()


async def cb_feedback(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    await choose_feedback_type(call.message)
