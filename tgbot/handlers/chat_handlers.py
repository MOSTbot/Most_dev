from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from tgbot.handlers import main_menu
from tgbot.handlers.section_descriptions import chat_handlers
from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.misc import SQLRequests
from tgbot.misc.utils import SectionName

CB_MENU_ITEMS: tuple[list[str], list[str]] = ['Еще аргумент', 'Еще вопросы', 'Оставить отзыв', 'Главное меню'], \
                                             ['more_arguments', 'thematic_questions', 'feedback', 'main_menu']

OTHER_QUESTIONS: tuple[list[str], list[str]] = ['Еще вопросы по теме', 'Главное меню'], \
                                               ['thematic_questions', 'main_menu']


def register_chat_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(chat_mode, commands=["chat"], state=None)
    dp.register_message_handler(chat_mode, Text(equals='💬 Режим диалога', ignore_case=True), state=None)
    dp.register_message_handler(assertions, lambda message: message.text in SQLRequests
                                .select_by_table_and_column('assertions', 'assertion_name'), state=None)
    dp.register_message_handler(a_questions, lambda message: message.text in SQLRequests
                                .select_by_table_and_column('a_assertions', 'a_assertion_name'), state=None)
    dp.register_callback_query_handler(thematic_questions, text='thematic_questions', state=None)
    dp.register_callback_query_handler(cb_more_args, text='more_arguments', state=None)
    dp.register_callback_query_handler(random_questions, text=['random_questions'], state=None)


async def chat_mode(message: Message) -> None:
    SectionName.s_name = 'Режим диалога'  # for logging purposes
    await  message.answer_photo(
        photo=open('tgbot/assets/chat.jpg', 'rb'),
        caption=chat_handlers['chat_mode']['caption'],
        reply_markup=ReplyMarkups.create_rm(2, True,
                                            *SQLRequests.select_by_table_and_column('assertions', 'assertion_name')))
    await  message.answer(chat_handlers['chat_mode']['answer'])


# WARNING: Catch exception 'Message text is empty' (Admin has not added any facts yet)
async def assertions(message: Message, state: FSMContext) -> None:  # These are callback-buttons!
    async with state.proxy() as data:
        data['message_text'], data['query'], data['counter'] = message.text, SQLRequests.get_facts(message.text), 0
        await  message.answer((data['query'][data['counter']][0]),
                              reply_markup=InlineMarkups.create_im(2, *CB_MENU_ITEMS))


async def cb_more_args(call: CallbackQuery, state: FSMContext) -> None | Message:  # FIXME: Needs refactoring
    try:
        await call.answer(cache_time=5)
        try:
            async with state.proxy() as data:
                if data['counter'] is None:
                    return await  call.message.answer('Аргументы на этот тезис закончились. '
                                                      'Хотите посмотреть дополнительные вопросы по теме?',
                                                      reply_markup=InlineMarkups.
                                                      create_im(2, *OTHER_QUESTIONS))
                data['counter'] += 1
                await call.message.answer((data['query'][data['counter']][0]),
                                          reply_markup=InlineMarkups.create_im(2, *CB_MENU_ITEMS))
        except (TypeError, KeyError):
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
            await main_menu(call.message, state)

    except IndexError:
        if data['message_text'] in SQLRequests.select_by_table_and_column('assertions', 'assertion_name'):
            await  call.message.answer('Аргументы на этот тезис закончились. '
                                       'Хотите посмотреть дополнительные вопросы по теме?',
                                       reply_markup=InlineMarkups.
                                       create_im(2, *OTHER_QUESTIONS))
            async with state.proxy() as data:
                data['counter'] = None
        elif data['message_text'] in SQLRequests.select_by_table_and_column('a_assertions', 'a_assertion_name'):
            other_questions = ReplyMarkups.create_rm(2, True, *SQLRequests.rnd_questions())
            await call.message.answer('Вы можете выбрать другие вопросы из меню ниже:', reply_markup=other_questions)
    return None


async def thematic_questions(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    async with state.proxy() as data:
        if get_assertions := SQLRequests.get_assertions(data['message_text']):  # if get_assertions != []
            await call.message.answer('Дополнительные вопросы, касающиеся данной темы ⬇',
                                      reply_markup=ReplyMarkups.create_rm(2, True, *get_assertions))
        else:
            await call.message.answer('Дополнительные вопросы, касающиеся данной темы ⬇',
                                      reply_markup=ReplyMarkups.create_rm(2, True, *SQLRequests.rnd_questions()))


async def a_questions(message: Message, state: FSMContext) -> None:  # These are callback-buttons!
    async with state.proxy() as data:
        data['message_text'], data['query'], data['counter'] = message.text, SQLRequests.get_ad_facts(message.text), 0
        try:
            await  message.answer((data['query'][data['counter']][0]),
                                  reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Еще вопросы',
                                                                           'Оставить отзыв', 'Главное меню'],
                                                                       ['more_arguments', 'random_questions',
                                                                        'feedback', 'main_menu']))
        except IndexError:
            await message.answer('Раздел находится в разработке',
                                 reply_markup=InlineMarkups.create_im(1, ['Главное меню'],
                                                                      ['main_menu']))
            await state.finish()


async def random_questions(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    other_questions = ReplyMarkups.create_rm(2, True, *SQLRequests.rnd_questions())
    await call.message.answer('Вы можете выбрать другие вопросы из меню ниже:', reply_markup=other_questions)
