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
    dp.register_message_handler(fsm_feedback, Text(contains='отзыв', ignore_case=True), state=None)
    dp.register_message_handler(fsm_feedback, commands=['feedback'], state=None)
    dp.register_message_handler(fsm_confirm_feedback, state=FSMFeedback.feedback)
    dp.register_message_handler(fsm_send_feedback, state=FSMFeedback.send_feedback)
    dp.register_message_handler(fsm_private_contacts, state=FSMFeedback.send_private_contacts)
    dp.register_callback_query_handler(cb_feedback, text='feedback', state=None)


async def fsm_feedback(message: Message) -> None:
    SectionName.s_name = 'Оставить отзыв'  # for logging purposes
    await  message.answer(
        'Напишите отзыв о нашем проекте ⬇', reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
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
    await  message.reply('Оставить отзыв?', reply_markup=ReplyMarkups.create_rm(2, True, 'Оставить отзыв', 'Отмена'))
    await FSMFeedback.next()


async def fsm_send_feedback(message: Message, state: FSMContext) -> None:  # TODO: Checking message for text only type!
    if message.text == 'Оставить отзыв':
        hash_user_id = HashData.hash_data(message.from_user.id)[54:]
        datetime = str(message.date)
        async with state.proxy() as data:
            SQLInserts.send_feedback(user_id=hash_user_id, datetime=datetime, feedback=data['user_feedback'])
        await message.answer('Спасибо, ваш отзыв отправлен! 🤗',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
        await message.answer('Большое спасибо за отзыв! Если вы хотите поделиться своей историей подробно '
                             'или связаться с нашей командой — напишите нам еще одно сообщение ниже ⬇\n\n'
                             'В этом сообщении мы сможем увидеть ваш <b>telegram ID</b>, чтобы написать вам напрямую. '
                             'Для конфиденциальности ваше сообщение будет сразу <b>удалено из чата</b>.\n\n'
                             'Если ничего не хотите писать - просто нажмите кнопку "Главное меню"\n\n'
                             'С уважением, команда «МОСТ».', reply_markup=ReplyMarkups
                             .create_rm(2, True, 'Главное меню'))
        async with state.proxy() as data:
            data['user_feedback'] = message.text
        await FSMFeedback.next()
    else:
        await message.answer('Вы отменили отправку отзыва!',
                             reply_markup=ReplyMarkups
                             .create_rm(2, True, *SQLRequests
                                        .select_by_table_and_column('main_menu', 'main_menu_name')))
        await message.delete()
        return await state.finish()


async def fsm_private_contacts(message: Message, state: FSMContext) -> Message | None:
    if message.text == 'Главное меню':
        from tgbot.handlers import main_menu
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        return await main_menu(message, state)  # type: ignore

    elif message.text in commands_list:
        await state.finish()
        return await message.answer('Действие отменено пользователем',
                                    reply_markup=ReplyMarkups
                                    .create_rm(2, True, *SQLRequests
                                               .select_by_table_and_column('main_menu', 'main_menu_name')))

    datetime = str(message.date)
    SQLInserts.send_feedback(user_id=message.from_user.id, datetime=datetime, feedback=message.text)
    await message.delete()
    await message.answer('Ваши контакты успешно отправлены, спасибо вам еще раз! ☺', reply_markup=ReplyMarkups
                         .create_rm(2, True, *SQLRequests
                                    .select_by_table_and_column('main_menu', 'main_menu_name')))
    return await state.finish()


async def cb_feedback(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    await fsm_feedback(call.message)
