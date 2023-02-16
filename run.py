import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.redis import RedisStorage2

from tgbot import load_config
from tgbot.handlers.registration import register_all_middlewares, register_all_filters, register_all_handlers, \
    register_all_bot_commands

from tgbot.misc import db, Disp, SearchIndex, SQLRequests

config = load_config(".env")
storage = RedisStorage2()
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')
Disp.disp = Dispatcher(bot, storage=storage)
SearchIndex.search_index = SQLRequests.get_search_index()

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
        await Disp.disp.storage.close()
        await Disp.disp.storage.wait_closed()
        await bot.session.close()
        db.close()  # type: ignore


logger = logging.getLogger(__name__)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
