from aiogram import Bot, Dispatcher

from tgbot.filters import SUFilter, AdFilter
from tgbot.handlers import register_main_menu_handlers, register_admin_handlers, register_feedback_handlers, \
    register_chat_handlers, register_practice_handlers, register_advice_handlers, register_theory_handlers, \
    register_other_handlers, register_echo
from tgbot.middlewares import LoggingMiddleware
from tgbot.misc import set_default_commands


def register_all_middlewares(dp: Dispatcher) -> None:
    dp.setup_middleware(LoggingMiddleware())


def register_all_filters(dp: Dispatcher) -> None:
    dp.filters_factory.bind(SUFilter)
    dp.filters_factory.bind(AdFilter)


async def register_all_bot_commands(dc: Bot) -> None:
    await set_default_commands(dc)


def register_all_handlers(dp: Dispatcher) -> None:
    register_admin_handlers(dp)
    register_feedback_handlers(dp)
    register_main_menu_handlers(dp)
    register_chat_handlers(dp)
    register_practice_handlers(dp)
    register_advice_handlers(dp)
    register_theory_handlers(dp)
    register_other_handlers(dp)
    register_echo(dp)
