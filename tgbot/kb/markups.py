from __future__ import annotations

from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton


class ReplyMarkups:
    @staticmethod
    def create_rm(row_width: int, one_time_keyboard: bool, *args: str) -> ReplyKeyboardMarkup:
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=row_width, one_time_keyboard=one_time_keyboard).add(
            *args)


class InlineMarkups:
    @staticmethod
    def create_im(row_width: int, button_name: list, callback: list, url: list | None = None) -> InlineKeyboardMarkup:
        try:
            dynamic_im = []
            for i in range(len(button_name)):
                if url is None:
                    dynamic_im.append(InlineKeyboardButton(button_name[i], callback_data=callback[i]))
                else:
                    dynamic_im.append(InlineKeyboardButton(button_name[i], callback_data=callback[i], url=url[i]))
            return InlineKeyboardMarkup(row_width=row_width).add(*dynamic_im)
        except IndexError as e:
            raise ValueError('Кнопок должно быть столько же сколько коллбэков и ссылок!') from e
