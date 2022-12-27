from __future__ import annotations

import logging
import logging.handlers

from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import CallbackQuery, Message

from tgbot.utils import SectionName, HashData, SQLRequests

# dict of cb buttons we're logging
# callback_dict = {'1': 'Первый вариант ответа',
#                  '2': 'Второй вариант ответа',
#                  '3': 'Третий вариант ответа',
#                  'main_menu': 'Главное меню',
#                  'like_btn': 'Поставил лайк',
#                  'dislike_btn': 'Поставил дизлайк',
#                  'more_arguments': 'Еще аргумент',
#                  'thematic_questions': 'Другие вопросы',
#                  'feedback': 'Оставить отзыв',
#                  'lets_go': 'Поехали! 🚀',
#                  'arguments_base': 'Перейти в базу аргументов'}

# list of rb buttons we're logging
# reply_list = [*SQLRequests.select_by_table_and_column('assertions', 'assertion_name'),
#               *SQLRequests.select_by_table_and_column('a_assertions', 'a_assertion_name'),
#               *SQLRequests.select_by_table_and_column('main_menu', 'main_menu_name'), 'Отмена',
#               '/start', '/menu', '/chat', '/practice', '/advice', '/theory', '/feedback', 'Оставить отзыв']


# class AdminsMiddleware(BaseMiddleware):
#
#     async def on_pre_process_update(self, update: Update, data: dict) -> None:
#         print(SQLRequests.all_admins_list())
#         return


# noinspection PyUnusedLocal
class LoggingMiddleware(BaseMiddleware):
    def __init__(self, logger: logging.Logger | str = __name__) -> None:
        if not isinstance(logger, logging.Logger):
            logger = logging.getLogger(logger)
            logger.setLevel(logging.INFO)
            sh = logging.StreamHandler()
            fh = logging.handlers.RotatingFileHandler('statistics.txt', mode='a', maxBytes=10 ** 7, backupCount=10,
                                                      encoding='UTF-8')
            formatter = logging.Formatter('%(asctime)s|%(message)s', datefmt='%m/%d/%Y %I:%M:%S')
            sh.setFormatter(formatter)
            fh.setFormatter(formatter)
            logger.addHandler(sh)
            logger.addHandler(fh)

        self.logger = logger

        super(LoggingMiddleware, self).__init__()

    async def on_post_process_callback_query(self, callback_query: CallbackQuery, results: list, data: dict) -> None:
        # if callback_query.data in callback_dict:
        hash_user_id = HashData.hash_data(callback_query.from_user.id)
        try:
            text = f"{hash_user_id[54:]}|{callback_query.data}|{str(callback_query.message.text[:96])}...|{SectionName.s_name}"
        except TypeError:
            text = f"{hash_user_id[54:]}|{callback_query.data}|Без сообщения|{SectionName.s_name}"
        self.logger.info(text.replace('\n', ' '))

    async def on_post_process_message(self, message: Message, results: list, data: dict) -> None:
        # if message.text in reply_list:
        hash_user_id = HashData.hash_data(message.from_user.id)
        if message.text == 'Оставить отзыв':
            text = f"{hash_user_id[54:]}|{message.text}|Отзыв оставлен пользователем!|{SectionName.s_name}"
        else:
            text = f"{hash_user_id[54:]}|{message.text}|Не доступно|{SectionName.s_name}"

        self.logger.info(text.replace('\n', ' '))
