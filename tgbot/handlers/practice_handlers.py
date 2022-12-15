import contextlib

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.kb import InlineMarkups, ReplyMarkups
from tgbot.utils import SQLRequests
from tgbot.utils.util_classes import MessageText


def register_practice_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(practice_mode, commands=["practice"], state=None)
    dp.register_message_handler(practice_mode,
                                Text(equals=['🏋️‍ Симулятор разговора', 'Сыграть еще раз!'], ignore_case=True),
                                state=None)
    dp.register_callback_query_handler(practice_start, text='lets_go', state=None)
    dp.register_callback_query_handler(practice_reaction, text=['1', '2', '3'], state=None)
    dp.register_callback_query_handler(practice_continue, text=['practice_continue'], state=None)
    dp.register_callback_query_handler(do_it_again, text=['do_it_again'], state=None)


async def practice_mode(message: Message) -> None:
    await  message.answer_photo(
        photo=open('tgbot/assets/practice.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме симулятор разговора.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Проверьте, насколько хорошо вы умеете бороться с пропагандой.'
                          ' Мы собрали для вас 10 мифов о войне и для каждого подобрали 3 варианта ответа —'
                          ' выберите верные, а бот МОСТ даст подробные комментарии.',
                          reply_markup=InlineMarkups.create_im(2, ['Поехали! 🚀', 'Главное меню'],
                                                               ['lets_go', 'main_menu']))


async def practice_start(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    if MessageText.flag is False and MessageText.score == 0:
        await call.answer(cache_time=5)
        cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
        MessageText.generator = SQLRequests.get_practice_questions()
        MessageText.value = next(MessageText.generator)
        MessageText.p_answers = SQLRequests.get_practice_answers(MessageText.value[1])  # type: ignore
        await  call.message.answer(MessageText.value[0], reply_markup=cases) # type: ignore
    else:
        await call.message.answer('Вы уже находитесь в режиме теста. Хотите начать сначала?',
                                  reply_markup=InlineMarkups.create_im(2, ['Сначала!', 'Продолжить тест'],
                                                                       ['do_it_again', 'practice_continue']))


async def practice_reaction(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    if MessageText.flag is False:
        MessageText.flag = True
        con = InlineMarkups.create_im(2, ['Продолжить', 'Отмена'], ['practice_continue', 'main_menu'])
        with contextlib.suppress(TypeError):
            if call.data == '1':
                MessageText.score = MessageText.score + int(MessageText.p_answers[0][1])
                await call.message.answer(MessageText.p_answers[0][0], reply_markup=con)
            elif call.data == '2':
                MessageText.score = MessageText.score + int(MessageText.p_answers[1][1])
                await call.message.answer(MessageText.p_answers[1][0], reply_markup=con)
            else:
                MessageText.score = MessageText.score + int(MessageText.p_answers[2][1])
                await call.message.answer(MessageText.p_answers[2][0], reply_markup=con)


async def practice_continue(call: CallbackQuery) -> None:
    try:
        await call.answer(cache_time=5)
        cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
        if MessageText.flag is True:
            MessageText.flag = False
            MessageText.value = next(MessageText.generator)
            MessageText.p_answers = SQLRequests.get_practice_answers(MessageText.value[1])
        else:
            await  call.message.answer('Пожалуйста, выберите один из предложенных вариантов ⬇')
        await  call.message.answer(MessageText.value[0], reply_markup=cases)
    except StopIteration:
        menu = ReplyMarkups.create_rm(3, True, 'Сыграть еще раз!', '🧠 Психология разговора',
                                      '📚 База аргументов', 'Главное меню')
        if MessageText.score < 8:
            await call.message.answer('<b>Убедить не получилось</b> 🙁\n'
                                      'Почитайте нашу базу аргументов и рекомендации психологов по ведению диалогов,'
                                      ' чтобы в следующий раз использовать бережную и проверенную аргументацию.',
                                      reply_markup=menu)
        elif 7 < MessageText.score < 15:
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
        MessageText.flag = False
        MessageText.score = 0


async def do_it_again(call: CallbackQuery) -> None:
    await call.answer(cache_time=5)
    MessageText.flag = False
    MessageText.score = 0
    await practice_mode(call.message)
