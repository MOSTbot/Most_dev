import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.utils import FSMFeedback, send_feedback, get_facts, get_assertions, select_by_table_and_column, \
    select_main_menu_description, find_value
from tgbot.utils.util_classes import MessageText

mt = MessageText()


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(fsm_feedback, Text(equals='🤓 Оставить отзыв', ignore_case=True), state=None)
    dp.register_message_handler(fsm_feedback, commands=['feedback'], state=None)
    dp.register_message_handler(fsm_confirm_feedback, state=FSMFeedback.feedback)
    dp.register_message_handler(fsm_send_feedback, state=FSMFeedback.send_feedback)
    dp.register_message_handler(start_handler, commands=["start"], state="*")
    dp.register_message_handler(chat_mode, commands=["chat"], state="*")
    dp.register_message_handler(chat_mode, Text(equals='💬 Режим диалога', ignore_case=True), state="*")
    dp.register_message_handler(questions, Text(equals=[*get_assertions()], ignore_case=True),
                                # WARNING: Here's the problem with dynamic update
                                state="*")  # WARNING: SQL option
    dp.register_callback_query_handler(cb_more_args, text='more_arguments', state="*")
    dp.register_callback_query_handler(cb_feedback, text='feedback', state="*")
    dp.register_message_handler(practice_mode, commands=["practice"], state="*")
    dp.register_message_handler(practice_mode, Text(equals='🏋️‍♂ Симулятор разговора', ignore_case=True), state="*")
    dp.register_message_handler(advice_mode, commands=["advice"], state="*")
    dp.register_message_handler(advice_mode, Text(equals='🧠 Психология разговора', ignore_case=True), state="*")
    dp.register_message_handler(advice_mode2, Text(equals=[*select_by_table_and_column('advice', 'topic_name')]),
                                state="*")  # WARNING: JSON option
    dp.register_message_handler(theory_mode, commands=["theory"], state="*")
    dp.register_message_handler(theory_mode, Text(equals='📚 База аргументов', ignore_case=True), state="*")
    dp.register_message_handler(text_wasnt_found, state="*")
    dp.register_callback_query_handler(cb_home, text='main_menu', state="*")


def user_log(user_id, message_text):
    return logging.info(f'{user_id=} {message_text=}')


# WARNING: Develop options for completing FSM. Not all state.finish() options have been explored
async def fsm_confirm_feedback(message: Message, state: FSMContext):
    if message.text in ['/start', '/chat', '/practice', '/advice', '/theory', '/feedback', '🤓 Оставить отзыв',
                        'Отмена']:
        await message.answer('Написание отзыва отменено пользователем',
                             reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu',
                                                                                                      'main_menu_name')))
        return await state.finish()
    async with state.proxy() as data: data['user_feedback'] = message.text
    await  message.answer('Оставить отзыв?', reply_markup=ReplyMarkups.create_rm(2, True, 'Оставить отзыв', 'Отмена'))
    await FSMFeedback.next()


async def fsm_feedback(message: Message):
    await  message.answer(
        'Напишите отзыв о нашем проекте ⬇', reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMFeedback.feedback.set()  # state: feedback
    # await message.delete()


async def fsm_send_feedback(message: Message, state: FSMContext):  # TODO: Checking message for text only type!
    if message.text == 'Оставить отзыв':
        user_id = message.from_user.id
        datetime = str(message.date)
        async with state.proxy() as data:
            send_feedback(user_id=user_id, datetime=datetime, feedback=data['user_feedback'])
        await message.answer('Спасибо, Ваш отзыв отправлен! 🤗', reply_markup=ReplyMarkups.create_rm(2, True,
                                                                                                     *select_by_table_and_column(
                                                                                                         'main_menu',
                                                                                                         'main_menu_name')))
    else:
        await message.answer('Вы отменили отправку отзыва!', reply_markup=ReplyMarkups.create_rm(2, True,
                                                                                                 *select_by_table_and_column(
                                                                                                     'main_menu',
                                                                                                     'main_menu_name')))
        await message.delete()
    return await state.finish()


async def start_handler(message: Message):
    # user_id = message.from_user.id
    # user_full_name = message.from_user.full_name
    # logging.info(f'{user_id=} {user_full_name=}')
    user_log(message.from_user.id, message.text)
    await message.answer_photo(
        photo=open('tgbot/assets/menu.jpg', 'rb'),
        caption='Какое направление вы хотите запустить?',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu', 'main_menu_name')))
    await message.answer(select_main_menu_description(),
                         reply_markup=InlineMarkups.create_im(2, ['Узнать больше о проекте'], ['some callback'], [
                             'https://relocation.guide/most']))  # FIXME: The link needs to be replaced
    await message.delete()


async def chat_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/chat.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме диалога. Отправляйте фразу или вопрос в чат и получайте аргументы,'
                ' которые помогают отделить ложь от правды. Оценивайте их силу, чтобы сделать МОСТ еще крепче.',
        reply_markup=ReplyMarkups.create_rm(3, True, *get_assertions()))
    await  message.answer('<i>Рассмотрим пример аргумента</i>\n\n'
                          'Собеседни_ца говорит вам: <b>«Мы многого не знаем, всё не так однозначно».</b>\n\n'
                          '<b>Фраза-мост — позволяет построить контакт с собеседником</b> ⬇\n'
                          'Соглашусь, что мы многого не знаем. Но мы точно знаем, что жизнь человека –'
                          ' высшая ценность общества, верно?\n\n'
                          '<b>Аргумент — конкретные примеры</b> ⬇\n'
                          'Я знаю одно: война несет смерть. Из-за войн страдают обычные люди.'
                          ' История научила нас этому, но почему-то мы думаем, что сможем провести войну без жертв.'
                          ' Так не бывает, к сожалению.\n\n'
                          '<b>Наводящий вопрос — продолжит диалог и запустит критическое мышление</b> ⬇\n'
                          'Что думаешь об этом?\n\n'
                          'Мы рекомендуем использовать три части ответа вместе, но по отдельности они тоже работают.\n\n'
                          'Выберите одну из предложенных тем ниже или введите свою в поле для ввода,'
                          ' чтобы получить аргумент. Например, «Путин знает, что делает» или «Это война с НАТО» ⬇')
    await message.delete()

# WARNING: Catch exception 'Message text is empty' (Admin has not added any facts yet)
async def questions(message: Message):  # These are callback-buttons!
    mt.message_text = message.text
    mt.message_text = get_facts(mt.message_text)  # SQL option
    await  message.reply(next(mt.message_text),
                         reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Другие вопросы', '👍', '👎',
                                                                  'Оставить отзыв', 'Главное меню'],
                                                              ['more_arguments', 'some callback', 'some callback',
                                                               'some callback', 'feedback',
                                                               'main_menu']))  # WARNING: Dynamic arguments can't be recognized!


async def cb_more_args(call: CallbackQuery):
    try:
        await call.answer(cache_time=5)
        await call.message.answer(next(mt.message_text),
                                  reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Другие вопросы', '👍', '👎',
                                                                           'Оставить отзыв', 'Главное меню'],
                                                                       ['more_arguments', 'some callback',
                                                                        'some callback',
                                                                        'some callback', 'feedback',
                                                                        'main_menu']))  # WARNING: Dynamic arguments can't be recognized!)
    except StopIteration:
        await  call.message.answer('Больше аргументов нет',
                                   reply_markup=InlineMarkups.create_im(2, ['Другие вопросы', 'Главное меню'],
                                                                        ['some callback',
                                                                         'main_menu']))  # For testing purposes


async def practice_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/practice.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме симулятор разговора.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Проверьте, насколько хорошо вы умеете бороться с пропагандой.'
                          ' Мы собрали для вас 10 мифов о войне и для каждого подобрали 3 варианта ответа —'
                          ' выберите верные, а бот МОСТ даст подробные комментарии.',
                          reply_markup=InlineMarkups.create_im(2, ['Поехали! 🚀', 'Главное меню'], ['sc', 'main_menu']))
    await message.delete()


async def advice_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/advice.jpg', 'rb'),
        caption='🟢 Собрали советы психологов о том, как не сойти с ума и говорить о войне с близкими,'
                ' чего ожидать, как реагировать и вести себя.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Выберите тему, чтобы прочитать ⬇',
                          reply_markup=ReplyMarkups.create_rm(3, True,
                                                              *select_by_table_and_column('advice', 'topic_name')))
    await message.delete()


# WARNING: JSON
async def advice_mode2(message: Message):
    await message.reply(find_value('advice', 'topic_description', 'topic_name', message.text),
                        reply_markup=ReplyMarkups.create_rm(3, True, *select_by_table_and_column('advice',
                                                                                                 'topic_name')))


async def theory_mode(message: Message):
    await message.answer('📚', reply_markup=ReplyKeyboardRemove())  # FIXME: This message is only for keyboard remove
    await  message.answer_photo(
        photo=open('tgbot/assets/theory.jpg', 'rb'),
        caption='Энциклопедия борца с пропагандой — самые полезные статьи, видео и аргументы.'
                ' Для тех, кто хочет детально разобраться в том, что происходит.',
        reply_markup=InlineMarkups.create_im(2, ['Перейти в базу аргументов', 'Главное меню'],
                                             ['sc', 'main_menu'], ['https://relocation.guide/most',
                                                                   None]))  # FIXME: The link needs to be replaced
    await message.delete()


async def cb_home(call: CallbackQuery):
    await call.answer(cache_time=10)
    await start_handler(call.message)


async def cb_feedback(call: CallbackQuery):
    await call.answer(cache_time=10)
    await fsm_feedback(call.message)


async def text_wasnt_found(message: Message):
    await  message.answer(
        'Извините, я не смог распознать вопрос. Попробуйте еще раз или воспользуйтесь меню ниже ⬇',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu', 'main_menu_name')))
