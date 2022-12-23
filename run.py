import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from tgbot import load_config
from tgbot.handlers.registration import register_all_middlewares, register_all_filters, register_all_handlers, \
    register_all_bot_commands

from tgbot.utils import db, Disp

config = load_config(".env")
storage = MemoryStorage()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
Disp.disp = Dispatcher(bot, storage=storage)


def update_dispatcher() -> None:
    Disp.disp = Dispatcher(bot, storage=storage)


async def main() -> None:
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format=u'%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s',
    # )
    # logger.info("Starting bot")

    bot['config'] = config

    register_all_middlewares(Disp.disp)
    register_all_filters(Disp.disp)
    register_all_handlers(Disp.disp)

    # Commands
    await register_all_bot_commands(bot)

    # Start polling
    try:
        await Disp.disp.start_polling()
    finally:
        await db.close() # type: ignore
        await Disp.disp.storage.close()
        await Disp.disp.storage.wait_closed()
        await bot.session.close()


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
