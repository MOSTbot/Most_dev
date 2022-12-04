from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
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


class InlineMarkups:

    @staticmethod
    def create_im(row_width: int, button_name: list, callback: list, url: list = None) -> InlineKeyboardMarkup:
        if len(button_name) != len(callback):
            raise ValueError('Кнопок должно быть столько же сколько их коллбэков!')
        dynamic_im = []
        for i in range(len(button_name)):
            if url is None:
                dynamic_im.append(InlineKeyboardButton(button_name[i], callback_data=callback[i]))
            else:
                dynamic_im.append(InlineKeyboardButton(button_name[i], callback_data=callback[i], url=url[i]))
        return InlineKeyboardMarkup(row_width=row_width).add(*dynamic_im)
