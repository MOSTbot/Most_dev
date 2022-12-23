from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.kb import ReplyMarkups
from tgbot.utils import FSMFeedback, SQLRequests, SQLInserts, SectionName


def register_feedback_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(fsm_feedback, Text(contains='отзыв', ignore_case=True), state=None)
    dp.register_message_handler(fsm_feedback, commands=['feedback'], state=None)
    dp.register_message_handler(fsm_confirm_feedback, state=FSMFeedback.feedback)
    dp.register_message_handler(fsm_send_feedback, state=FSMFeedback.send_feedback)
    dp.register_callback_query_handler(cb_feedback, text='feedback', state=None)


async def fsm_feedback(message: Message) -> None:
    SectionName.s_name = 'Оставить отзыв'
    await  message.answer(
        'Напишите отзыв о нашем проекте ⬇', reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMFeedback.feedback.set()  # state: feedback


# WARNING: Develop options for completing FSM. Not all state.finish() options have been explored
async def fsm_confirm_feedback(message: Message, state: FSMContext) -> None:
    if message.text in ['/start', '/menu', '/chat', '/practice', '/advice', '/theory', '/feedback', '🤓 Оставить отзыв',
                        'Отмена']:
        await message.answer('Написание отзыва отменено пользователем',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
        return await state.finish()
    async with state.proxy() as data: data['user_feedback'] = message.text
    await  message.reply('Оставить отзыв?', reply_markup=ReplyMarkups.create_rm(2, True, 'Оставить отзыв', 'Отмена'))
    await FSMFeedback.next()


async def fsm_send_feedback(message: Message, state: FSMContext) -> None:  # TODO: Checking message for text only type!
    if message.text == 'Оставить отзыв':
        user_id = message.from_user.id
        datetime = str(message.date)
        async with state.proxy() as data:
            SQLInserts.send_feedback(user_id=user_id, datetime=datetime, feedback=data['user_feedback'])
        await message.answer('Спасибо, Ваш отзыв отправлен! 🤗',
                             reply_markup=ReplyMarkups
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
    await fsm_feedback(call.message)
