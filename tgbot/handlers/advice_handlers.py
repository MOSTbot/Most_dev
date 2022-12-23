from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.kb import ReplyMarkups
from tgbot.utils import SQLRequests, SectionName


def register_advice_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(advice_mode, commands=["advice"], state=None)
    dp.register_message_handler(advice_mode, Text(equals='🧠 Психология разговора', ignore_case=True), state=None)
    dp.register_message_handler(advice_mode2, Text(equals=SQLRequests
                                                   .select_by_table_and_column('advice', 'topic_name')), state=None)


async def advice_mode(message: Message) -> None:
    SectionName.s_name = 'Психология разговора'
    await  message.answer_photo(
        photo=open('tgbot/assets/advice.jpg', 'rb'),
        caption='🟢 Собрали советы психологов о том, как не сойти с ума и говорить о войне с близкими,'
                ' чего ожидать, как реагировать и вести себя.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('Выберите тему, чтобы прочитать ⬇',
                          reply_markup=ReplyMarkups
                          .create_rm(2, True, *SQLRequests.select_by_table_and_column('advice', 'topic_name')))
    await message.delete()


async def advice_mode2(message: Message) -> None:
    await message.reply(
        *SQLRequests.select_by_table_and_column('advice', 'topic_description', 'topic_name', message.text),
        reply_markup=ReplyMarkups
        .create_rm(2, True, *SQLRequests.select_by_table_and_column('advice', 'topic_name')))
