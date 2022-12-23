from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery

from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.utils import FSMAddAdmin, FSMDeleteAdmin, FSMAddAssertion, SQLInserts, SQLRequests, SQLDeletions


def register_admin_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(update_disp, text='update_dispatcher', state='*', is_su=True)
    dp.register_message_handler(admin_start, commands=["start"], state=None, is_su=True)
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
    # --------------------- ADD ASSERTION --------------------
    dp.register_callback_query_handler(assertion_init, text='add_section_ib', state='*', is_su=True)
    dp.register_message_handler(check_assertion, state=FSMAddAssertion.initialize, is_su=True)
    dp.register_message_handler(add__assertion, state=FSMAddAssertion.add_assertion, is_su=True)
    dp.register_message_handler(facts_init, state=FSMAddAssertion.facts_init, is_su=True)
    dp.register_message_handler(add__facts, state=FSMAddAssertion.add_facts, is_su=True)


async def admin_start(message: Message) -> None:
    await message.answer_photo(photo=open('tgbot/assets/start.jpg', 'rb'))
    await message.answer('<b>Мы ответственны за тех, кого приручила пропаганда</b>.\n'
                         'Особенно за родных, любимых и друзей.\n\n'
                         'Разве не достаточно просто сказать правду?\n'
                         'Увы, многие сталкивались с тем, что '
                         '<b>правду не слышат или не хотят слышать</b>. Но это не повод сдаваться.\n\n'
                         'МОСТ — cовместный проект <a href="https://relocation.guide/">гайда в свободный мир</a> и XZ foundation. '
                         'Это сценарии разговоров с близкими о войне.\n\n'
                         'Их разработали волонтеры гайда <b>с опытом переубеждения</b> близких, а '
                         '<b>психологи, социологи и журналисты</b> добавили научную базу.\n\n'
                         'Разговор о войне не будет простым и быстрым.\n\n'
                         'Мы верим, что <b>экспертный подход, общественный вклад и эмпатия</b> помогут «вернуть связь» '
                         'с близкими и создать продукт, который основан на способности слышать, '
                         'мыслить и противостоять ложным мнениям.',
                         reply_markup=InlineMarkups.create_im(1, ['Перейти в главное меню'], ['main_menu']))
    await message.answer("Вы являетесь Администратором бота",
                         reply_markup=InlineMarkups.create_im(2, ['Добавить Администратора',
                                                                  'Удалить Администратора',
                                                                  'Список Администраторов',
                                                                  'Последние 10 отзывов',
                                                                  'Добавить раздел',
                                                                  'Обновить данные'],
                                                              ['admin_promote_ib',
                                                               'admin_remove_ib',
                                                               'admins_list_ib',
                                                               'last_10_feedbacks_ib',
                                                               'add_section_ib',
                                                               'update_dispatcher']))


# ------------------ UPDATE DYNAMIC DATA -----------------
async def update_disp(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    from run import update_dispatcher
    update_dispatcher()
    await call.message.answer('Данные были успешно обновлены')


# ------------------- PROMOTE TO ADMIN -------------------
async def add_new_admin(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer('Укажите ID добавляемого Администратора:')
    await FSMAddAdmin.add_admin_id.set()


async def new_admin_id(message: Message, state: FSMContext) -> None:  # state: add_admin_id
    if message.text.isdigit() and 5 <= len(message.text) <= 10:
        async with state.proxy() as data:
            data['admin_id'] = message.text
            await message.answer('Укажите имя добавляемого Администратора:')
            await FSMAddAdmin.next()
    else:
        await message.answer('ID Администратора должно быть целым числом, не менее 5 и не более 10 знаков!')


async def new_admin_name(message: Message, state: FSMContext) -> None:  # state: add_admin_name
    if not message.text.isdigit() and 3 <= len(message.text) <= 15:
        async with state.proxy() as data:
            data['admin_name'] = message.text
            await message.answer(
                f"Добавить\n\nИмя: <b>{data['admin_name']}</b>, ID: <b>{data['admin_id']}</b>\n\nв базу данных Администраторов?",
                reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))
        await FSMAddAdmin.next()
    else:
        await message.answer('Имя Администратора должно быть строкой, не менее 3-х и не более 15 символов!')


async def new_admin_confirm(message: Message, state: FSMContext) -> None:  # state: confirm
    if message.text == 'Добавить':
        async with state.proxy() as data:
            if await SQLInserts.create_admin(admin_id=data['admin_id'], admin_name=data['admin_name']) is False:
                await message.answer('Администратор с данным ID существует!'
                                     ' Если хотите изменить имя, то удалите этого'
                                     ' Администратора и добавьте его снова с другим именем')
                await message.delete()
                return await state.finish()
            await message.answer('Администратор добавлен')
            return await message.delete()
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
    await call.message.answer('Укажите последние 10 знаков хеша удаляемого Администратора:')
    await FSMDeleteAdmin.delete_admin_id.set()


async def delete_admin_id(message: Message, state: FSMContext) -> None:  # state: delete_admin_id
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
            if await SQLDeletions.delete_from_table(table='list_of_admins', column='admin_id', value=data['admin_id']):
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
    # await call.message.answer(*SQLRequests.all_admins_list()) # for testing purpuses


# ------------------- LAST 10 FEEDBACKS ------------------
async def last_10_feedbacks(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer(SQLRequests.last10_fb())


# --------------------- ADD ASSERTION --------------------
async def assertion_init(call: CallbackQuery) -> None:
    await call.answer(cache_time=10)
    await call.message.answer('Выберете существующее утверждение или напишите новое',
                              reply_markup=ReplyMarkups
                              .create_rm(3, True,
                                         *SQLRequests.select_by_table_and_column('assertions', 'assertion_name')))
    await FSMAddAssertion.initialize.set()


async def check_assertion(message: Message, state: FSMContext) -> None:  # state: initialize
    assertion = SQLRequests.check_if_item_exists(table='assertions', column='assertion_name', value=message.text)
    async with state.proxy() as data:
        data['assertion'] = message.text
    if assertion is False:
        await message.answer('Этого аргумента нет в базе данных. Добавить?',
                             reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))
        return await FSMAddAssertion.add_assertion.set()  # state: add_assertion
    await message.answer('Напишите контрагрументы к этому утверждению, по одному за раз:',
                         reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMAddAssertion.facts_init.set()  # If the argument is in the database, switch to adding facts to this argument


async def add__assertion(message: Message, state: FSMContext) -> None:  # state: add_assertion
    if message.text == 'Добавить':
        await message.delete()
        async with state.proxy() as data:
            await SQLInserts.add_to_table(table='assertions', column='assertion_name', value=data['assertion'])
            await message.answer('Аргумент был добавлен в базу данных')
            await message.answer('Напишите контрагрументы по одному за раз и нажмите Enter')
            await FSMAddAssertion.facts_init.set()
    else:
        await message.answer('Действие отменено')
        await state.finish()


async def facts_init(message: Message, state: FSMContext) -> None:  # state: facts_init
    if message.text == 'Отмена':
        await message.delete()
        await message.answer('Действие отменено')
        return await state.finish()
    async with state.proxy() as data:
        data['fact'] = message.text
    await message.answer(f'Подтвердите добавление контраргумента в базу данных:\n\n{message.text}',
                         reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))

    await FSMAddAssertion.add_facts.set()


async def add__facts(message: Message, state: FSMContext) -> None:  # state: add_facts
    # TODO: Should be a check if the fact exists in the database
    if message.text == 'Добавить':
        async with state.proxy() as data:
            await SQLInserts.add_to_child_table(parent_table='assertions', parent_table_pk_column='assertion_id',
                                                parent_table_column='assertion_name',
                                                parent_table_value=data['assertion'],
                                                child_table='facts', child_table_column='fact_name',
                                                child_table_value=data['fact'])
            await message.answer('Факт был добавлен в базу данных.\n\nДобавьте следующий контрагргумент'
                                 ' или нажмите "Отмена"', reply_markup=ReplyMarkups.create_rm(2, True, 'Отмена'))
            await FSMAddAssertion.facts_init.set()
    else:
        await message.answer('Действие отменено')
        await state.finish()
