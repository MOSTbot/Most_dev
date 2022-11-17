import json, logging, os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, ParseMode, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, \
    CallbackQuery
from aiogram.dispatcher.filters import Text

API_TOKEN = os.getenv('BOT_TOKEN')

# Configure logging
logging.basicConfig(level=logging.INFO, filename='bot_log.log')
# TODO: Configure user actions logging

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN, parse_mode='html')
dp = Dispatcher(bot)

# --------------------------- JSON ----------------------------
with open('questions.json', 'r') as file:
    questions_answers_json = json.load(file)

with open('advice.json', 'r') as file:
    advice_json = json.load(file)

question_keys = questions_answers_json.keys()  # Extract question_keys from dict
advice_keys = advice_json.keys()  # Extract advise_keys from dict

# ----------------------- REGULAR MENU ------------------------

questions_markup = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
                    .add(*question_keys))  # Dialogue questions

main_markup = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
               .add('💬 Режим диалога', '🏋️‍♂ Симулятор разговора', '🧠 Психология разговора', '📚 База аргументов')
               .row('🤓 Оставить отзыв'))

home_btn = KeyboardButton('Вернуться в главное меню ↩')
return_markup = ReplyKeyboardMarkup(resize_keyboard=True).row(home_btn)  # Leading back to the main menu

advice_markup = ReplyKeyboardMarkup(resize_keyboard=True).add(*advice_keys)

# ------------------------ INLINE MENU ------------------------
more_args_inln_btn = InlineKeyboardButton('Еще аргумент', callback_data='give_me_arguments')
more_quests_inln_btn = InlineKeyboardButton('Еще вопрос', callback_data='some callback')
like_inln_btn = InlineKeyboardButton('👍', callback_data='some callback')
dislike_inln_btn = InlineKeyboardButton('👎', callback_data='some callback')
feedback_inln_btn = InlineKeyboardButton('Оставить отзыв', callback_data='some callback')
arg_db_inln_btn = InlineKeyboardButton('Перейти в базу аргументов', callback_data='external_reference',
                                       url='https://relocation.guide/most')  # FIXME The link needs to be replaced
home_inln_btn = InlineKeyboardButton('Вернуться в главное меню ↩', callback_data='main_menu')

dialogue_inln_markup = (InlineKeyboardMarkup(row_width=2)
                        .add(more_args_inln_btn, more_quests_inln_btn)
                        .add(like_inln_btn, dislike_inln_btn)
                        .row(feedback_inln_btn))

theory_inln_markup = (InlineKeyboardMarkup()
                      .row(arg_db_inln_btn)
                      .row(home_inln_btn))


# -------------------- CALLBACK HANDLERS ----------------------
@dp.callback_query_handler(text='external_reference')
async def callback_arg_db_inln_btn(call: CallbackQuery):
    await call.answer(cache_time=10)


@dp.callback_query_handler(text='main_menu')
async def callback_home_inln_btn(call: CallbackQuery):
    await call.answer(cache_time=10)
    await start_handler(call.message)


# --------------------- MESSAGE HANDLERS ----------------------
@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    user_full_name = message.from_user.full_name
    logging.info(f'{user_id=} {user_full_name=}')

    await message.answer_photo(
        # TODO: Add photo ids to the appropriate list
        photo='AgACAgIAAxkBAAEaAo5jdMo3w3PzcGd8WAPERpuMCYU6aAACmcwxGwUmqUsuOzhZ3YjMvwEAAwIAA3MAAysE',
        caption='Какое направление вы хотите запустить?')
    await message.answer("💬 <b>Режим диалога</b>\n Подобрать подходящие аргументы.\n\n"
                         "🏋️‍♂ <b>Симулятор разговора</b>\n Подготовиться к реальному диалогу и проверить свои знания.\n\n"
                         "🧠 <b>Психология разговора</b>\n Узнать, как бережно говорить с близкими.\n\n"
                         "📚 <b>База аргументов</b>\n Прочитать все аргументы в одном месте.\n\n"
                         "🤓 <b>Оставить отзыв</b>\n Поделиться мнением о проекте.", reply_markup=main_markup)


# TODO: JSON does not allow wrapping links, so the text will look slightly worse than in the constructor

@dp.message_handler(commands=['chat'])
@dp.message_handler(Text(equals='💬 Режим диалога'))
async def dialog_mode(message: types.Message):
    await  message.answer_photo(
        photo="AgACAgIAAxkBAAEaAsZjdM8Y_KXF9-ssyr5wl3et_2XJvAACu8wxGwUmqUtBsWahHEFkZgEAAwIAA3MAAysE",
        caption='🟢 МОСТ работает в режиме диалога. Отправляйте фразу или вопрос в чат и получайте аргументы,'
                ' которые помогают отделить ложь от правды. Оценивайте их силу, чтобы сделать МОСТ еще крепче.')
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
                          ' чтобы получить аргумент. Например, «Путин знает, что делает» или «Это война с НАТО» ⬇',
                          reply_markup=questions_markup)


@dp.message_handler(commands=['practice'])
@dp.message_handler(Text(equals='🏋️‍♂ Симулятор разговора'))
async def dialog_mode(message: types.Message):
    await  message.answer_photo(
        photo="AgACAgIAAxkBAAEaA8FjdO1utUgbzQMZt_DGNTSYSj6GiQACSL4xG1qJqUugWOSv5-VzeQEAAwIAA3MAAysE",
        caption='🟢 МОСТ работает в режиме симулятор разговора.')
    await  message.answer('Проверьте, насколько хорошо вы умеете бороться с пропагандой.'
                          ' Мы собрали для вас 10 мифов о войне и для каждого подобрали 3 варианта ответа —'
                          ' выберите верные, а бот МОСТ даст подробные комментарии.',
                          reply_markup=types.ReplyKeyboardRemove())


@dp.message_handler(commands=['advice'])
@dp.message_handler(Text(equals='🧠 Психология разговора'))
async def advice_mode(message: types.Message):
    await  message.answer_photo(
        # TODO: if-else statement when photo is not found
        photo="AgACAgIAAxkBAAEaA9ljdO_uOD1eGSrKJ6IfEx5oYrH5SQACVr4xG1qJqUsuemllaMkO8wEAAwIAA3MAAysE",
        caption='🟢 Собрали советы психологов о том, как не сойти с ума и говорить о войне с близкими,'
                ' чего ожидать, как реагировать и вести себя.', reply_markup=types.ReplyKeyboardRemove())
    await  message.answer('Выберите тему, чтобы прочитать ⬇',
                          reply_markup=advice_markup)


@dp.message_handler(commands=['theory'])
@dp.message_handler(Text(equals='📚 База аргументов'))
async def advice_mode(message: types.Message):
    await  message.answer_photo(
        photo="AgACAgIAAxkBAAEaBQRjdRityX2vqAP6s_KNFo7wfAOp7AACKL8xG1qJqUu5AkIe0ljE4AEAAwIAA3MAAysE",
        caption='Энциклопедия борца с пропагандой — самые полезные статьи, видео и аргументы.'
                ' Для тех, кто хочет детально разобраться в том, что происходит.',
        reply_markup=theory_inln_markup)


@dp.message_handler()
async def all_the_modes_qa(message: types.Message):
    if message.text in questions_answers_json:
        # FIXME: This behavior requires more discussion. Perhaps you should pass JSON with a pre-formatted string
        msg = '<b>Фраза-мост</b> ⬇\n' + questions_answers_json[message.text][0] \
              + '\n\n<b>Аргумент ⬇</b>\n' + questions_answers_json[message.text][1] \
              + '\n\n<b>Наводящий вопрос ⬇</b>\n' + questions_answers_json[message.text][2]
        await  message.answer('💬', reply_markup=return_markup)
        await  message.answer(msg, reply_markup=dialogue_inln_markup)
    elif message.text in advice_keys:
        for i in advice_json[message.text]: await message.answer(i)
    elif message.text == "Вернуться в главное меню ↩":
        await  start_handler(message)  # Back to start
    elif message.text == "📚 База аргументов":
        await  message.answer('Раздел в разработке', reply_markup=main_markup)
    else:
        await  message.answer('Извините, я не смог распознать вопрос. Воспользуйтесь меню ниже ⬇',
                              reply_markup=questions_markup)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
