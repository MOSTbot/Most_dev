from aiogram.types import ReplyKeyboardMarkup
from tgbot.json.json_utils import advice_keys
from tgbot.utils import get_assertions

# ------------------- MARKUPS -------------------
advice_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
             .add(*advice_keys))


class ReplyMarkups:
    @staticmethod
    def questions_rm() -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True).add(*get_assertions())

    @staticmethod
    def create_rm(row_width: int, one_time_keyboard: bool, *args: str) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width, one_time_keyboard=one_time_keyboard).add(
            *args)
