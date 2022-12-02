from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# ------------------- BUTTONS -------------------
more_quests_ib = InlineKeyboardButton('Другие вопросы', callback_data='some callback')
like_ib = InlineKeyboardButton('👍', callback_data='some callback')
dislike_ib = InlineKeyboardButton('👎', callback_data='some callback')
feedback_ib = InlineKeyboardButton('Оставить отзыв', callback_data='feedback')
arg_base_ib = InlineKeyboardButton('Перейти в базу аргументов', callback_data='external_reference',
                                   url='https://relocation.guide/most')  # FIXME: The link needs to be replaced
home_ib = InlineKeyboardButton('Главное меню', callback_data='main_menu')
more_args_ib = InlineKeyboardButton('Еще аргумент', callback_data='more_arguments')
# ----------------- ADMIN MENU ------------------
add_section_ib = InlineKeyboardButton('Добавить раздел', callback_data='add_section_ib')
get_json_ib = InlineKeyboardButton('Получить JSON', callback_data='get_json_ib')
admins_list_ib = InlineKeyboardButton('Список Администраторов', callback_data='admins_list_ib')
admin_promote_ib = InlineKeyboardButton('Добавить Администратора', callback_data='admin_promote_ib')
admin_remove_ib = InlineKeyboardButton('Удалить Администратора', callback_data='admin_remove_ib')
last_10_fb_ib = InlineKeyboardButton('Последние 10 отзывов', callback_data='last_10_feedbacks_ib')
about_project_ib = InlineKeyboardButton('Узнать больше о проекте', callback_data='more_about_project',
                                        url='https://relocation.guide/most')  # FIXME: The link needs to be replaced)

# ------------------- MARKUPS -------------------
theory_im = InlineKeyboardMarkup().add(arg_base_ib, home_ib)
dialogue_im = (InlineKeyboardMarkup(row_width=2)
               .add(more_args_ib, more_quests_ib,
                    like_ib, dislike_ib,
                    feedback_ib, home_ib))
chat_no_more_args_im = InlineKeyboardMarkup().add(home_ib, more_quests_ib)
admin_menu_im = (InlineKeyboardMarkup(row_width=2)
                 .add(add_section_ib)
                 .add(admin_promote_ib, admin_remove_ib)
                 .add(admins_list_ib, last_10_fb_ib))
home_im = InlineKeyboardMarkup().add(home_ib)
about_project_im = InlineKeyboardMarkup().add(about_project_ib)
