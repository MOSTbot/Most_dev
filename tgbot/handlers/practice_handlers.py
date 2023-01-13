import contextlib

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.handlers import main_menu
from tgbot.kb import InlineMarkups, ReplyMarkups
from tgbot.utils import SQLRequests, GetPracticeQuestions
from tgbot.utils.util_classes import SectionName


def register_practice_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(practice_mode, commands=["practice"], state="*")
    dp.register_message_handler(practice_mode,
                                Text(equals=['🏋 Симулятор разговора', 'Сыграть еще раз!'], ignore_case=True),
                                state="*")
    dp.register_callback_query_handler(practice_start, text='lets_go', state="*")
    dp.register_callback_query_handler(practice_reaction, text=['1', '2', '3'], state="*")
    dp.register_callback_query_handler(practice_continue, text=['practice_continue'], state="*")
    dp.register_callback_query_handler(do_it_again, text=['do_it_again'], state="*")


async def practice_mode(message: Message, state: FSMContext) -> None:
    SectionName.s_name = 'Симулятор разговора'  # for logging purposes
    async with state.proxy() as data:
        data['flag'], data['score'], data['p_generator'], data['value'] = False, 0, None, None
    await  message.answer_photo(
        photo=open('tgbot/assets/practice.jpg', 'rb'),
        caption='🟢 МОСТ работает в режиме симулятор разговора.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Проверьте, насколько хорошо вы умеете бороться с пропагандой.'
                          ' Мы собрали для вас 10 мифов о войне и для каждого подобрали 3 варианта ответа —'
                          ' выберите верные, а бот МОСТ даст подробные комментарии.',
                          reply_markup=InlineMarkups.create_im(2, ['Поехали! 🚀', 'Главное меню'],
                                                               ['lets_go', 'main_menu']))


async def practice_start(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    try:
        async with state.proxy() as data:
            if data['flag'] is False and data['score'] == 0:
                await call.answer(cache_time=5)
                cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
                data['p_generator'] = GetPracticeQuestions()
                data['value'] = next(data['p_generator'])
                data['p_answers'] = SQLRequests.get_practice_answers(data['value'][1])  # type: ignore
                await  call.message.answer(data['value'][0], reply_markup=cases)  # type: ignore
            else:
                await call.message.answer('Вы уже находитесь в режиме теста. Хотите начать сначала?',
                                          reply_markup=InlineMarkups.create_im(2, ['Сначала!', 'Продолжить тест'],
                                                                               ['do_it_again', 'practice_continue']))
    except KeyError:
        current_state = await state.get_state()
        if current_state is not None:
            await state.finish()
        await main_menu(call.message, state)


async def practice_reaction(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    async with state.proxy() as data:

        try:
            if data['flag'] is False:
                data['flag'] = True
                con = InlineMarkups.create_im(2, ['Продолжить', 'Отмена'], ['practice_continue', 'main_menu'])
                with contextlib.suppress(TypeError):
                    if call.data == '1':
                        data['score'] = data['score'] + int(data['p_answers'][0][1])
                        await call.message.answer(data['p_answers'][0][0], reply_markup=con)
                    elif call.data == '2':
                        data['score'] = data['score'] + int(data['p_answers'][1][1])
                        await call.message.answer(data['p_answers'][1][0], reply_markup=con)
                    else:
                        data['score'] = data['score'] + int(data['p_answers'][2][1])
                        await call.message.answer(data['p_answers'][2][0], reply_markup=con)
        except KeyError:
            current_state = await state.get_state()
            if current_state is not None:
                await state.finish()
            await main_menu(call.message, state)


async def practice_continue(call: CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:

        try:
            await call.answer(cache_time=5)
            cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])

            try:
                if data['flag'] is True and 'value' in data.keys():
                    data['flag'] = False
                    data['value'] = next(data['p_generator'])
                    data['p_answers'] = SQLRequests.get_practice_answers(data['value'][1])
                elif 'value' not in data.keys():
                    return await main_menu(call.message, state)
                else:
                    await  call.message.answer('Пожалуйста, выберите один из предложенных вариантов ⬇')
            except KeyError:
                current_state = await state.get_state()
                if current_state is not None:
                    await state.finish()
                await main_menu(call.message, state)

            await  call.message.answer(data['value'][0], reply_markup=cases)

        except StopIteration:
            menu = ReplyMarkups.create_rm(3, True, 'Сыграть еще раз!', '🧠 Психология разговора',
                                          '📚 База аргументов', 'Главное меню')
            if data['score'] < 8:
                await call.message.answer('<b>Убедить не получилось</b> 🙁\n'
                                          'Почитайте нашу базу аргументов и рекомендации психологов по ведению диалогов,'
                                          ' чтобы в следующий раз использовать бережную и проверенную аргументацию.',
                                          reply_markup=menu)
            elif 7 < data['score'] < 15:
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
            data['flag'], data['score'] = False, 0


async def do_it_again(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    async with state.proxy() as data:
        data['flag'], data['score'], data['p_generator'], data['value'] = False, 0, None, None
    await practice_start(call, state)
