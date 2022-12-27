from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove

from tgbot.kb import InlineMarkups
from tgbot.utils import SectionName


def register_theory_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(theory_mode, commands=["theory"], state=None)
    dp.register_message_handler(theory_mode, Text(equals='📚 База аргументов', ignore_case=True), state=None)


async def theory_mode(message: Message) -> None:
    SectionName.s_name = 'База аргументов'  # for logging purposes
    await message.answer('Энциклопедия борца с пропагандой — самые полезные статьи, видео и аргументы. '
                         'Для тех, кто хочет детально разобраться в том, что происходит.',
                         reply_markup=ReplyKeyboardRemove())
    await  message.answer_photo(photo=open('tgbot/assets/theory.jpg', 'rb'),
        reply_markup=InlineMarkups.create_im(2, ['Перейти в базу аргументов', 'Главное меню'],
                                             ['arguments_base', 'main_menu'], ['https://relocation.guide/most', None]))
    # FIXME: The link needs to be replaced
