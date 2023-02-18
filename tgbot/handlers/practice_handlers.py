import contextlib

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.handlers.section_descriptions import practice_handlers
from tgbot.handlers import main_menu
from tgbot.kb import InlineMarkups, ReplyMarkups
from tgbot.misc import SQLRequests
from tgbot.misc.utils import SectionName


def register_practice_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(practice_mode, commands=["practice"], state="*")
    dp.register_message_handler(practice_mode,
                                Text(equals=['🏋 Режим тренажера', 'Сыграть еще раз!'], ignore_case=True),
                                state="*")
    dp.register_callback_query_handler(practice_start, text='lets_go', state="*")
    dp.register_callback_query_handler(practice_reaction, text=['1', '2', '3'], state="*")
    dp.register_callback_query_handler(practice_continue, text=['practice_continue'], state="*")
    dp.register_callback_query_handler(do_it_again, text=['do_it_again'], state="*")


async def practice_mode(message: Message, state: FSMContext) -> None:
    SectionName.s_name = 'Симулятор разговора'  # for logging purposes
    async with state.proxy() as data:
        data['p_flag'], data['score'], data['p_query'], data['question'], data['p_counter'] = False, 0, None, None, 0
    await  message.answer_photo(
        photo=open('tgbot/assets/practice.jpg', 'rb'),
        caption=practice_handlers['practice_mode']['caption'], reply_markup=ReplyKeyboardRemove())
    await  message.answer(practice_handlers['practice_mode']['answer'],
                          reply_markup=InlineMarkups.create_im(2, ['Поехали! 🚀', 'Главное меню'],
                                                               ['lets_go', 'main_menu']))


async def practice_start(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    try:
        async with state.proxy() as data:
            if data['p_flag'] is False and data['score'] == 0:
                await call.answer(cache_time=5)
                cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])
                data['p_query'] = SQLRequests.get_practice_questions()
                # WARNING! If the table is empty IndexError is raised!
                data['question'] = data['p_query'][data['p_counter']]
                data['p_answers'] = SQLRequests.get_practice_answers(data['question'][1])  # type: ignore
                await  call.message.answer(data['question'][0], reply_markup=cases)  # type: ignore
            else:
                await call.message.answer('Вы уже находитесь в режиме теста. Хотите начать сначала?',
                                          reply_markup=InlineMarkups.create_im(2, ['Сначала!', 'Продолжить тест'],
                                                                               ['do_it_again', 'practice_continue']))
    except (KeyError, IndexError):
        return await key_error(call, state)


async def practice_reaction(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    async with state.proxy() as data:
        try:
            if data['p_flag'] is False:
                data['p_flag'] = True
                con = InlineMarkups.create_im(2, ['Продолжить', 'Главное меню'], ['practice_continue', 'main_menu'])
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
            return await key_error(call, state)


async def practice_continue(call: CallbackQuery, state: FSMContext) -> None:
    async with state.proxy() as data:
        try:
            if data['p_counter'] == len(data['p_query']) - 1:
                menu = ReplyMarkups.create_rm(3, True, 'Сыграть еще раз!', '🧠 Психология разговора',
                                              '📚 База аргументов', 'Главное меню')
                if data['score'] < 8:
                    await call.message.answer(practice_handlers['practice_continue']['answer1'],
                                              reply_markup=menu)
                elif 7 < data['score'] < 15:
                    await call.message.answer(practice_handlers['practice_continue']['answer2'],
                                              reply_markup=menu)
                else:
                    await call.message.answer(practice_handlers['practice_continue']['answer3'],
                                              reply_markup=InlineMarkups.create_im(1, ['Главное меню'], ['main_menu']))
                data['p_flag'], data['score'], data['p_counter'] = False, 0, 0
                return
        except KeyError:
            return await key_error(call, state)

        await call.answer(cache_time=5)
        cases = InlineMarkups.create_im(3, ['1', '2', '3'], ['1', '2', '3'])

        try:
            if data['p_flag'] is True and 'question' in data.keys():
                data['p_flag'] = False
                data['p_counter'] += 1
                data['question'] = data['p_query'][data['p_counter']]
                data['p_answers'] = SQLRequests.get_practice_answers(data['question'][1])
            elif 'question' not in data.keys():
                return await main_menu(call.message, state)
            else:
                await  call.message.answer('Пожалуйста, выберите один из предложенных вариантов ⬇')
        except KeyError:
            return await key_error(call, state)
        try:
            await  call.message.answer(data['question'][0], reply_markup=cases)
        except KeyError:
            return await key_error(call, state)


async def do_it_again(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    async with state.proxy() as data:
        data['p_flag'], data['score'], data['p_query'], data['question'], data['p_counter'] = False, 0, None, None, 0
    await practice_start(call, state)


async def key_error(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer(cache_time=5)
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
    await call.message.answer('Кажется что-то пошло не так... Пожалуйста, '
                              'попробуйте еще раз или вернитесь в главное меню',
                              reply_markup=InlineMarkups.create_im(1, ['Главное меню'], ['main_menu']))
