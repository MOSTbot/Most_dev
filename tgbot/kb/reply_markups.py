from aiogram.types import ReplyKeyboardMarkup
from tgbot.json.json_utils import question_keys, advice_keys
from tgbot.utils import get_assertions

# ------------------- MARKUPS -------------------
questions_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
                .add(*get_assertions())) # SQL вариант
# questions_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
#                 .add(*question_keys)) # JSON вариант
main_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
           # TODO: Dynamic menu from JSON
           .add('💬 Режим диалога', '🏋️‍♂ Симулятор разговора', '🧠 Психология разговора', '📚 База аргументов')
           .row('🤓 Оставить отзыв'))
home_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
           .add(
    'Вернуться в главное меню ↩'))  # TODO: Add inline menu instead ("Главное меню, "Список вопросов", "Оставить отзыв")
advice_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
             .add(*advice_keys))
feedback_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
               .add('Отправить отзыв', 'Отмена'))
add_item_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
               .add('Добавить', 'Отмена'))
remove_admin_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
                   .add('Удалить', 'Отмена'))
continue_or_cancel = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, one_time_keyboard=True)
                      .add('Продолжить', 'Отмена'))
cancel_rm = (ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
                      .add('Отмена'))

class ReplyMarkups:
    @staticmethod
    def questions_rm():
        return ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True).add(*get_assertions())