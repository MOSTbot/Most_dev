import contextlib
import logging

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.utils import FSMFeedback, send_feedback, get_facts, get_assertions, select_by_table_and_column, \
    select_main_menu_description, get_a_facts, get_practice_questions, get_practice_answers, rnd_questions
from tgbot.utils.util_classes import MessageText, UtilValues

mt = MessageText()


def register_user_handlers(dp: Dispatcher):
    dp.register_message_handler(fsm_feedback, Text(contains='отзыв', ignore_case=True), state=None)
    dp.register_message_handler(fsm_feedback, commands=['feedback'], state=None)
    dp.register_message_handler(fsm_confirm_feedback, state=FSMFeedback.feedback)
    dp.register_message_handler(fsm_send_feedback, state=FSMFeedback.send_feedback)
    dp.register_message_handler(start, commands=["start"], state=None)
    dp.register_message_handler(menu_handler, commands=["menu"], state=None)
    dp.register_message_handler(menu_handler, Text(contains='Главное меню', ignore_case=True), state=None)
    dp.register_message_handler(chat_mode, commands=["chat"], state=None)
    dp.register_message_handler(chat_mode, Text(equals='💬 Режим диалога', ignore_case=True), state=None)
    dp.register_message_handler(questions, Text(equals=select_by_table_and_column('assertions', 'assertion_name'),
                                                ignore_case=True),
                                state=None)  # WARNING: Here's the problem with dynamic update
    dp.register_message_handler(a_questions, Text(equals=select_by_table_and_column('a_assertions', 'a_assertion_name'),
                                                  ignore_case=True),
                                state=None)
    dp.register_callback_query_handler(thematic_questions, text='thematic_questions', state=None)
    dp.register_callback_query_handler(cb_more_args, text='more_arguments', state=None)
    dp.register_callback_query_handler(cb_feedback, text='feedback', state=None)
    dp.register_message_handler(practice_mode, commands=["practice"], state=None)
    dp.register_message_handler(practice_mode,
                                Text(equals=['🏋️‍ Симулятор разговора', 'Сыграть еще раз!'], ignore_case=True),
                                state=None)
    dp.register_message_handler(advice_mode, commands=["advice"], state=None)
    dp.register_message_handler(advice_mode, Text(equals='🧠 Психология разговора', ignore_case=True), state=None)
    dp.register_message_handler(advice_mode2, Text(equals=select_by_table_and_column('advice', 'topic_name')),
                                state=None)
    dp.register_message_handler(theory_mode, commands=["theory"], state=None)
    dp.register_message_handler(theory_mode, Text(equals='📚 База аргументов', ignore_case=True), state=None)
    dp.register_message_handler(text_wasnt_found, state=None)
    dp.register_callback_query_handler(cb_home, text='main_menu', state=None)
    dp.register_callback_query_handler(practice_start, text='lets_go', state=None)
    dp.register_callback_query_handler(practice_reaction, text=['1', '2', '3'], state=None)
    dp.register_callback_query_handler(practice_continue, text=['practice_continue'], state=None)
    dp.register_callback_query_handler(do_it_again, text=['do_it_again'], state=None)
    dp.register_callback_query_handler(random_questions, text=['random_questions'], state=None)


def user_log(user_id, message_text):
    return logging.info(f'{user_id=} {message_text=}')


async def fsm_feedback(message: Message):
    await  message.answer(
        'Напишите отзыв о нашем проекте ⬇', reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMFeedback.feedback.set()  # state: feedback


# WARNING: Develop options for completing FSM. Not all state.finish() options have been explored
async def fsm_confirm_feedback(message: Message, state: FSMContext):
    if message.text in ['/start', '/menu', '/chat', '/practice', '/advice', '/theory', '/feedback', '🤓 Оставить отзыв',
                        'Отмена']:
        await message.answer('Написание отзыва отменено пользователем',
                             reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu',
                                                                                                      'main_menu_name')))
        return await state.finish()
    async with state.proxy() as data: data['user_feedback'] = message.text
    await  message.reply('Оставить отзыв?', reply_markup=ReplyMarkups.create_rm(2, True, 'Оставить отзыв', 'Отмена'))
    await FSMFeedback.next()


async def fsm_send_feedback(message: Message, state: FSMContext):  # TODO: Checking message for text only type!
    if message.text == 'Оставить отзыв':
        user_id = message.from_user.id
        datetime = str(message.date)
        async with state.proxy() as data:
            send_feedback(user_id=user_id, datetime=datetime, feedback=data['user_feedback'])
        await message.answer('Спасибо, Ваш отзыв отправлен! 🤗',
                             reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu',
                                                                                                      'main_menu_name')))
    else:
        await message.answer('Вы отменили отправку отзыва!',
                             reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu',
                                                                                                      'main_menu_name')))
        await message.delete()
    return await state.finish()


async def start(message: Message):
    await message.answer_photo(photo=open('tgbot/assets/start.jpg', 'rb'))
    await message.answer('<b>Мы ответственны за тех, кого приручила пропаганда</b>.\n'
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
                         reply_markup=InlineMarkups.create_im(1, ['Перейти в главное меню'], ['main_menu']))


async def menu_handler(message: Message):
    mt.flag = False
    # user_id = message.from_user.id
    # user_full_name = message.from_user.full_name
    # logging.info(f'{user_id=} {user_full_name=}')
    # user_log(message.from_user.id, message.text)
    await message.answer_photo(
        photo=open('tgbot/assets/menu.jpg', 'rb'),
        caption='Какое направление вы хотите запустить?',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu', 'main_menu_name')))
    await message.answer(select_main_menu_description(),
                         reply_markup=InlineMarkups.create_im(2, ['Узнать больше о проекте'], ['some callback'], [
                             'https://relocation.guide/most']))  # FIXME: The link needs to be replaced


async def chat_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/chat.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме диалога. Отправляйте фразу или вопрос в чат и получайте аргументы,'
                ' которые помогают отделить ложь от правды. Оценивайте их силу, чтобы сделать МОСТ еще крепче.',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('assertions', 'assertion_name')))
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


# WARNING: Catch exception 'Message text is empty' (Admin has not added any facts yet)
async def questions(message: Message):  # These are callback-buttons!
    mt.message_text = message.text
    mt.generator = get_facts(mt.message_text)  # SQL option
    await  message.reply(next(mt.generator),
                         reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Другие вопросы', '👍', '👎',
                                                                  'Оставить отзыв', 'Главное меню'],
                                                              ['more_arguments', 'thematic_questions', 'some callback',
                                                               'some callback', 'feedback',
                                                               'main_menu']))  # WARNING: Dynamic arguments can't be recognized!


async def cb_more_args(call: CallbackQuery):
    try:
        await call.answer(cache_time=5)
        await call.message.answer(next(mt.generator),
                                  reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Другие вопросы', '👍', '👎',
                                                                           'Оставить отзыв', 'Главное меню'],
                                                                       ['more_arguments', 'thematic_questions',
                                                                        'some callback',
                                                                        'some callback', 'feedback',
                                                                        'main_menu']))  # WARNING: Dynamic arguments can't be recognized!
    except StopIteration:
        if mt.message_text in select_by_table_and_column('assertions', 'assertion_name'):
            await  call.message.answer('Хотите посмотреть дополнительные вопросы по теме?',
                                       reply_markup=InlineMarkups.
                                       create_im(2, ['Другие вопросы по теме', 'Главное меню'],
                                                 ['thematic_questions',
                                                  'main_menu']))
        elif mt.message_text in select_by_table_and_column('a_assertions', 'a_assertion_name'):
            other_questions = ReplyMarkups.create_rm(2, True, *rnd_questions())
            await call.message.answer('Вы можете выбрать другие вопросы из меню ниже:', reply_markup=other_questions)


async def thematic_questions(call: CallbackQuery):
    await call.answer(cache_time=5)
    await call.message.answer('Дополнительные вопросы, касающиеся данной темы ⬇',
                              reply_markup=ReplyMarkups.create_rm(2, True, *get_assertions(mt.message_text)))


async def a_questions(message: Message):  # These are callback-buttons!
    mt.message_text = message.text
    mt.generator = get_a_facts(mt.message_text)
    await  message.reply(next(mt.generator),
                         reply_markup=InlineMarkups.create_im(2, ['Еще аргумент', 'Другие вопросы', '👍', '👎',
                                                                  'Оставить отзыв', 'Главное меню'],
                                                              ['more_arguments', 'random_questions', 'some callback',
                                                               'some callback', 'feedback',
                                                               'main_menu']))  # WARNING: Dynamic arguments can't be recognized!


async def practice_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/practice.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме симулятор разговора.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Проверьте, насколько хорошо вы умеете бороться с пропагандой.'
                          ' Мы собрали для вас 10 мифов о войне и для каждого подобрали 3 варианта ответа —'
                          ' выберите верные, а бот МОСТ даст подробные комментарии.',
                          reply_markup=InlineMarkups.create_im(2, ['Поехали! 🚀', 'Главное меню'],
                                                               ['lets_go', 'main_menu']))


async def advice_mode(message: Message):
    await  message.answer_photo(
        photo=open('tgbot/assets/advice.jpg', 'rb'),
        caption='🟢 Собрали советы психологов о том, как не сойти с ума и говорить о войне с близкими,'
                ' чего ожидать, как реагировать и вести себя.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Выберите тему, чтобы прочитать ⬇',
                          reply_markup=ReplyMarkups.create_rm(2, True,
                                                              *select_by_table_and_column('advice', 'topic_name')))
    await message.delete()


async def advice_mode2(message: Message):
    await message.reply(*select_by_table_and_column('advice', 'topic_description', 'topic_name', message.text),
                        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('advice',
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


async def cb_home(call: CallbackQuery):
    await call.answer(cache_time=5)
    await menu_handler(call.message)


async def cb_feedback(call: CallbackQuery):
    await call.answer(cache_time=5)
    await fsm_feedback(call.message)


async def practice_start(call: CallbackQuery):
    await call.answer(cache_time=5)
    if mt.flag is False and mt.score == 0:
        await call.answer(cache_time=5)
        cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
        mt.generator = get_practice_questions()
        mt.value = next(mt.generator)
        mt.p_answers = get_practice_answers(mt.value[1])
        await  call.message.answer(mt.value[0], reply_markup=cases)
    else:
        await call.message.answer('Вы уже находитесь в режиме теста. Хотите начать сначала?',
                                  reply_markup=InlineMarkups.create_im(2, ['Сначала!', 'Продолжить тест'],
                                                                       ['do_it_again', 'practice_continue']))


async def practice_reaction(call: CallbackQuery):
    await call.answer(cache_time=5)
    if mt.flag is False:
        mt.flag = True
        con = InlineMarkups.create_im(2, ['Продолжить', 'Отмена'], ['practice_continue', 'main_menu'])
        with contextlib.suppress(TypeError):
            if call.data == '1':
                mt.score = mt.score + mt.p_answers[0][1]
                await call.message.answer(mt.p_answers[0][0], reply_markup=con)
            elif call.data == '2':
                mt.score = mt.score + mt.p_answers[1][1]
                await call.message.answer(mt.p_answers[1][0], reply_markup=con)
            else:
                mt.score = mt.score + mt.p_answers[2][1]
                await call.message.answer(mt.p_answers[2][0], reply_markup=con)


async def practice_continue(call: CallbackQuery):
    try:
        await call.answer(cache_time=5)
        cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
        if mt.flag is True:
            mt.flag = False
            mt.value = next(mt.generator)
            mt.p_answers = get_practice_answers(mt.value[1])
        else:
            await  call.message.answer('Пожалуйста, выберите один из предложенных вариантов ⬇')
        await  call.message.answer(mt.value[0], reply_markup=cases)
    except StopIteration:
        menu = ReplyMarkups.create_rm(3, True, 'Сыграть еще раз!', '🧠 Психология разговора',
                                      '📚 База аргументов', 'Главное меню')
        if mt.score < 8:
            await call.message.answer('<b>Убедить не получилось</b> 🙁\n'
                                      'Почитайте нашу базу аргументов и рекомендации психологов по ведению диалогов,'
                                      ' чтобы в следующий раз использовать бережную и проверенную аргументацию.',
                                      reply_markup=menu)
        elif 7 < mt.score < 15:
            await call.message.answer('<b>На верном пути!</b> ❗\n'
                                      'Вы смогли ответить почти на все тезисы. '
                                      'Почитайте нашу базу аргументов и рекомендации психологов по ведению диалогов,'
                                      ' чтобы в следующий раз иметь ответ на любой вопрос.',
                                      reply_markup=menu)
        else:
            await call.message.answer('<b>Оппонент убежден!</b> ✅\n'
                                      'Бережность, открытость и проверенная информация '
                                      '– то, что вам помогло это сделать. Браво.',
                                      reply_markup=InlineMarkups.create_im(1, ['Главное меню'], ['main_menu']))
        mt.flag = False
        mt.score = 0


async def do_it_again(call: CallbackQuery):
    await call.answer(cache_time=5)
    mt.flag = False
    mt.score = 0
    await practice_mode(call.message)


async def random_questions(call: CallbackQuery):
    await call.answer(cache_time=5)
    other_questions = ReplyMarkups.create_rm(2, True, *rnd_questions())
    await call.message.answer('Вы можете выбрать другие вопросы из меню ниже:', reply_markup=other_questions)


async def text_wasnt_found(message: Message):
    await  message.answer(
        'Извините, я не смог распознать вопрос. Попробуйте еще раз или воспользуйтесь меню ниже ⬇',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu', 'main_menu_name')))
