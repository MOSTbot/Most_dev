from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeDefault


async def set_default_commands(bot: Bot):
    return await bot.set_my_commands(commands=[
        BotCommand('start', 'Главное меню'),
        BotCommand('chat', '💬 Режим диалога'),
        BotCommand('practice', '🏋️‍♂ Симулятор разговора'),
        BotCommand('advice', '🧠 Психология разговора'),
        BotCommand('theory', '📚 База аргументов'),
        BotCommand('feedback', '🤓 Оставить отзыв')],
        scope=BotCommandScopeDefault())




