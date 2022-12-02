import asyncio, logging
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot import load_config
from tgbot.filters import SUFilter
from tgbot.utils import set_default_commands, db
from tgbot.handlers import register_admin_handlers, register_user_handlers, register_echo
from tgbot.middlewares.environment import EnvironmentMiddleware, AdminsMiddleware


def register_all_middlewares(dp, config):
    dp.setup_middleware(EnvironmentMiddleware(config=config))
    dp.setup_middleware(AdminsMiddleware())


def register_all_filters(dp):
    dp.filters_factory.bind(SUFilter)


def register_all_handlers(dp):
    register_admin_handlers(dp)
    register_user_handlers(dp)
    register_echo(dp)


async def register_all_bot_commands(bot: Bot):
    await set_default_commands(bot)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    )
    logger.info("Starting bot")
    config = load_config(".env")

    storage = MemoryStorage()
    bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
    dp = Dispatcher(bot, storage=storage)

    bot['config'] = config

    register_all_middlewares(dp, config)
    register_all_filters(dp)
    register_all_handlers(dp)

    # Commands
    await register_all_bot_commands(bot)

    # Start polling
    try:
        await dp.start_polling()
    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()
        await db.close() # WARNING! Closing Database


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
