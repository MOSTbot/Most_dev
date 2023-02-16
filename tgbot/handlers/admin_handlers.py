from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

from tgbot.api import GoogleSheetsAPI

from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.misc import FSMAddAdmin, FSMDeleteAdmin, SQLInserts, SQLRequests, SQLDeletions, clear_cache_globally


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_message_handler(su_start, commands=["admin"], state=None, is_su=True)
    dp.register_message_handler(admin_start, commands=["admin"], state=None, is_admin=True)
    # ------------------- GET DATA FROM API ------------------
    dp.register_callback_query_handler(get_data_from_gs, text='get_data_from_gs', state='*', is_su=True)
    dp.register_callback_query_handler(get_data_from_gs, text='get_data_from_gs', state='*', is_admin=True)
    # --------------------- CANCEL BUTTON --------------------
    dp.register_message_handler(cancel_btn, Text(equals='Отмена'), state='*', is_su=True)
    # ------------------- PROMOTE TO ADMIN -------------------
    dp.register_callback_query_handler(add_new_admin, text='admin_promote_ib', state='*', is_su=True)
    dp.register_message_handler(new_admin_id, state=FSMAddAdmin.add_admin_id, is_su=True)
    dp.register_message_handler(new_admin_name, state=FSMAddAdmin.add_admin_name, is_su=True)
    dp.register_message_handler(new_admin_confirm, state=FSMAddAdmin.confirm, is_su=True)
    # --------------------- REMOVE ADMIN ---------------------
    dp.register_callback_query_handler(delete_admin_from_list, text='admin_remove_ib', state='*', is_su=True)
    dp.register_message_handler(delete_admin_id, state=FSMDeleteAdmin.delete_admin_id, is_su=True)
    dp.register_message_handler(delete_admin_confirm, state=FSMDeleteAdmin.confirm, is_su=True)
    # ------------------- SELECT ALL ADMINS ------------------
    dp.register_callback_query_handler(select_admins, text='admins_list_ib', state='*', is_su=True)
    # ------------------- LAST 10 FEEDBACKS ------------------
    dp.register_callback_query_handler(last_10_feedbacks, text='last_10_feedbacks_ib', state='*', is_su=True)
    dp.register_callback_query_handler(last_10_feedbacks, text='last_10_feedbacks_ib', state='*', is_admin=True)
    # ---------------------- CLEAR CACHE ---------------------
    dp.register_callback_query_handler(clear_cache, text='clear_global_cache', state='*', is_su=True)


async def su_start(message: Message) -> None:
    await message.answer("Вы являетесь Глобальным Администратором",
                         reply_markup=InlineMarkups.create_im(1, ['Добавить Администратора',
                                                                  'Удалить Администратора',
                                                                  'Список Администраторов',
                                                                  'Последние 10 отзывов',
                                                                  'Обновить данные из API',
                                                                  'Очистить глобальный кэш'],
                                                              ['admin_promote_ib',
                                                               'admin_remove_ib',
                                                               'admins_list_ib',
                                                               'last_10_feedbacks_ib',
                                                               'get_data_from_gs',
                                                               'clear_global_cache']))


async def admin_start(message: Message) -> None:
    await message.answer("Вы являетесь Администратором",
                         reply_markup=InlineMarkups.create_im(1, ['Последние 10 отзывов',
                                                                  'Обновить данные из API'],
                                                              ['last_10_feedbacks_ib',
                                                               'get_data_from_gs']))


# ------------------- GET DATA FROM API ------------------
async def get_data_from_gs(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    rng = 'B2:E'
    shts = ['assertions', 'facts',
            'a_assertions', 'a_facts',
            'main_menu', 'data_privacy',
            'practice_questions', 'practice_answers',
            'adv_assertions', 'adv_answers',
            'notifications']
    await GoogleSheetsAPI.get_data(rng, shts, call)


# ------------------- PROMOTE TO ADMIN -------------------
async def add_new_admin(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer('Укажите ID добавляемого Администратора:',
                              reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMAddAdmin.add_admin_id.set()


async def new_admin_id(message: Message, state: FSMContext) -> None:  # state: add_admin_id
    await message.delete()
    if message.text.isdigit() and 5 <= len(message.text) <= 10:
        async with state.proxy() as data:
            data['admin_id'] = message.text
            await message.answer('Укажите имя добавляемого Администратора:',
                                 reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
            await FSMAddAdmin.next()
    else:
        await message.answer('ID Администратора должно быть целым числом, не менее 5 и не более 10 знаков!',
                             reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))


async def new_admin_name(message: Message, state: FSMContext) -> None:  # state: add_admin_name
    await message.delete()
    if not message.text.isdigit() and 3 <= len(message.text) <= 15:
        async with state.proxy() as data:
            data['admin_name'] = message.text
            await message.answer(
                "Добавить Администратора?",
                reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))
        await FSMAddAdmin.next()
    else:
        await message.answer('Имя Администратора должно быть строкой, не менее 3-х и не более 15 символов!',
                             reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))


async def new_admin_confirm(message: Message, state: FSMContext) -> None:  # state: confirm
    if message.text == 'Добавить':
        await message.delete()
        async with state.proxy() as data:
            if SQLInserts.create_admin(admin_id=data['admin_id'], admin_name=data['admin_name']) is False:
                await message.answer('Администратор с данным хешем существует!'
                                     ' Если хотите изменить имя, то удалите этого'
                                     ' Администратора и добавьте его снова с другим именем',
                                     reply_markup=ReplyKeyboardRemove())
                return await state.finish()
            await message.answer('Администратор добавлен')
    else:
        await message.delete()
        await message.answer('Администратор не был добавлен')
    await state.finish()


# --------------------- REMOVE ADMIN ---------------------
async def delete_admin_from_list(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    admins_list = SQLRequests.select_all_admins()
    if admins_list == 'Список Администраторов пуст':
        await call.message.answer('Список Администраторов пуст - удалять некого 😱')
        return
    await call.answer(cache_time=10)
    await call.message.answer('Укажите последние 10 знаков хеша удаляемого Администратора:',
                              reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMDeleteAdmin.delete_admin_id.set()


async def delete_admin_id(message: Message, state: FSMContext) -> None:  # state: delete_admin_id
    await message.delete()
    if len(message.text) == 10:
        async with state.proxy() as data:
            data['admin_id'] = message.text
            await message.answer("Подтвердите удаление:",
                                 reply_markup=ReplyMarkups.create_rm(2, True, 'Удалить', 'Отмена'))
            await FSMDeleteAdmin.next()
    else:
        await message.answer('Хеш Администратора должен состоять из 10 символов!')


# state: confirm
async def delete_admin_confirm(message: Message, state: FSMContext) -> None:
    if message.text == 'Удалить':
        async with state.proxy() as data:
            if SQLDeletions.delete_from_table(table='list_of_admins', column='admin_id', value=data['admin_id']):
                await message.answer('Администратор удален')
                await message.delete()
                return await state.finish()
            await message.answer('Администратор не найден в базе данных, удаление невозможно!')
            return await message.delete()
    else:
        await message.delete()
        await message.answer('Администратор не был удален')
    await state.finish()


# ------------------- SELECT ALL ADMINS ------------------
async def select_admins(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer(SQLRequests.select_all_admins())


# ------------------- LAST 10 FEEDBACKS ------------------
async def last_10_feedbacks(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer(SQLRequests.last10_fb())


async def cancel_btn(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()
        await message.answer('Действие отменено', reply_markup=ReplyKeyboardRemove())


# ---------------------- CLEAR CACHE ---------------------
async def clear_cache(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await clear_cache_globally()
    await call.message.answer('Кэш успешно очищен')
