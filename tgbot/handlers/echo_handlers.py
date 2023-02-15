from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext

from tgbot.handlers import fsm_feedback


async def bot_echo_all(message: types.Message, state: FSMContext) -> None:
    await message.answer('Ели вы видите это сообщение, то вы сделали что-то очень нестандартное... '
                         'Может сообщите нам, как вы сюда попали? 😊')
    await fsm_feedback(message, state)


def register_echo(dp: Dispatcher) -> None:
    dp.register_message_handler(bot_echo_all, state="*", content_types=types.ContentTypes.ANY)
