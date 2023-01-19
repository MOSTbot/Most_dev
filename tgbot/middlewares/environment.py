from __future__ import annotations

import logging
import logging.handlers

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from tgbot.utils import SectionName, HashData

# noinspection PyUnusedLocal
class LoggingMiddleware(BaseMiddleware):
    def __init__(self, logger: logging.Logger | str = __name__) -> None:
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)
            logger.setLevel(logging.INFO)
            sh = logging.StreamHandler()
            fh = logging.handlers.RotatingFileHandler('statistics.log', mode='a', maxBytes=10 ** 7, backupCount=10,
                                                      encoding='UTF-8')
            formatter = logging.Formatter('%(asctime)s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S')
            sh.setFormatter(formatter)
            fh.setFormatter(formatter)
            logger.addHandler(sh)
            logger.addHandler(fh)

        self.logger = logger

        super(LoggingMiddleware, self).__init__()

    async def on_post_process_callback_query(self, callback_query: CallbackQuery, results: list, data: dict) -> None:
        hash_user_id = HashData.hash_data(callback_query.from_user.id)
        try:
            text = f"{hash_user_id[54:]}|{callback_query.data}|{str(callback_query.message.text[:96])}...|{SectionName.s_name}"
        except TypeError:
            text = f"{hash_user_id[54:]}|{callback_query.data}|Без сообщения|{SectionName.s_name}"
        self.logger.info(text.replace('\n', ' '))

    async def on_post_process_message(self, message: Message, results: list, data: dict) -> None:
        hash_user_id = HashData.hash_data(message.from_user.id)
        if message.text == 'Оставить отзыв':
            text = f"{hash_user_id[54:]}|{message.text}|Отзыв оставлен пользователем!|{SectionName.s_name}"
        else:
            text = f"{hash_user_id[54:]}|{message.text}|Не доступно|{SectionName.s_name}"

        self.logger.info(text.replace('\n', ' '))
