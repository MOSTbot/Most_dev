from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
# from tgbot.handlers import start_handler
from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.utils import create_admin, FSMAddAdmin, FSMDeleteAdmin, select_all_admins, last10_fb, \
    FSMAddAssertion, check_if_item_exists, add_to_child_table, delete_from_table, add_to_table, \
    select_by_table_and_column, get_assertions


async def admin_start(message: Message):
    await message.answer_photo(
        photo=open('tgbot/assets/menu.jpg', 'rb'),
        caption='Какое направление вы хотите запустить?',
        reply_markup=ReplyMarkups.create_rm(2, True, *select_by_table_and_column('main_menu', 'main_menu_name')))
    await message.answer("💬 <b>Режим диалога</b>\n Подобрать подходящие аргументы.\n\n"
                         "🏋️‍♂ <b>Симулятор разговора</b>\n Подготовиться к реальному диалогу и проверить свои знания.\n\n"
                         "🧠 <b>Психология разговора</b>\n Узнать, как бережно говорить с близкими.\n\n"
                         "📚 <b>База аргументов</b>\n Прочитать все аргументы в одном месте.\n\n"
                         "🤓 <b>Оставить отзыв</b>\n Поделиться мнением о проекте.",
                         reply_markup=InlineMarkups.create_im(1, ['Узнать больше о проекте'], ['more_about_project'],
                                                              ['https://relocation.guide/most']))
    await message.delete()
    await message.answer("Вы являетесь Администратором бота", reply_markup=InlineMarkups.create_im(2,
                                                                                                   [
                                                                                                       'Добавить Администратора',
                                                                                                       'Удалить Администратора',
                                                                                                       'Список Администраторов',
                                                                                                       'Последние 10 отзывов',
                                                                                                       'Добавить раздел'],
                                                                                                   ['admin_promote_ib',
                                                                                                    'admin_remove_ib',
                                                                                                    'admins_list_ib',
                                                                                                    'last_10_feedbacks_ib',
                                                                                                    'add_section_ib']))


# ------------------- PROMOTE TO ADMIN -------------------
async def add_new_admin(call: CallbackQuery):
    await call.answer(cache_time=10)
    await call.message.answer('Укажите ID добавляемого Администратора:')
    await FSMAddAdmin.add_admin_id.set()


async def new_admin_id(message: Message, state: FSMContext):  # state: add_admin_id
    if message.text.isdigit() and 5 <= len(message.text) <= 10:
        async with state.proxy() as data:
            data['admin_id'] = message.text
            await message.answer('Укажите имя добавляемого Администратора:')
            await FSMAddAdmin.next()
    else:
        await message.answer('ID Администратора должно быть целым числом, не менее 5 и не более 10 знаков!')


async def new_admin_name(message: Message, state: FSMContext):  # state: add_admin_name
    if not message.text.isdigit() and 3 <= len(message.text) <= 15:
        async with state.proxy() as data:
            data['admin_name'] = message.text
            await message.answer(
                f"Добавить\n\nИмя: <b>{data['admin_name']}</b>, ID: <b>{data['admin_id']}</b>\n\nв базу данных Администраторов?",
                reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))
        await FSMAddAdmin.next()
    else:
        await message.answer('Имя Администратора должно быть строкой, не менее 3-х и не более 15 символов!')


async def new_admin_confirm(message: Message, state: FSMContext):  # state: confirm
    if message.text == 'Добавить':
        async with state.proxy() as data:
            if await create_admin(admin_id=data['admin_id'], admin_name=data['admin_name']) is False:
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
async def delete_admin_from_list(call: CallbackQuery):  # TODO: Check if list is empty
    admins_list = select_all_admins()
    if admins_list == 'Список Администраторов пуст':
        return await call.message.answer('Список Администраторов пуст - удалять некого 😱')
    await call.answer(cache_time=10)
    await call.message.answer('Укажите полный хеш удаляемого Администратора:')
    await FSMDeleteAdmin.delete_admin_id.set()


async def delete_admin_id(message: Message, state: FSMContext):  # state: delete_admin_id
    if len(message.text) == 64:
        async with state.proxy() as data:
            data['admin_id'] = message.text
            await message.answer("Подтвердите удаление:",
                                 reply_markup=ReplyMarkups.create_rm(2, True, 'Удалить', 'Отмена'))
            await FSMDeleteAdmin.next()
    else:
        await message.answer('Хеш Администратора должен состоять из 64 символов!')


async def delete_admin_confirm(message: Message, state: FSMContext):  # state: confirm
    if message.text == 'Удалить':
        async with state.proxy() as data:
            if await delete_from_table(table='list_of_admins', column='admin_id', value=data['admin_id']):
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
async def select_admins(call: CallbackQuery):
    await call.answer(cache_time=10)
    await call.message.answer(select_all_admins())
    # await call.message.answer(all_admins_list()) # for testing purpuses


# ------------------- LAST 10 FEEDBACKS ------------------
async def last_10_feedbacks(call: CallbackQuery):
    await call.answer(cache_time=10)
    await call.message.answer(last10_fb())


# --------------------- ADD ASSERTION --------------------
async def assertion_init(call: CallbackQuery):
    await call.answer(cache_time=10)
    await call.message.answer('Выберете существующее утверждение или напишите новое',
                              reply_markup=ReplyMarkups.create_rm(3, True, *get_assertions()))
    await FSMAddAssertion.initialize.set()


async def check_assertion(message: Message, state: FSMContext):  # state: initialize
    assertion = check_if_item_exists(table='assertions', column='assertion_name', value=message.text)
    async with state.proxy() as data:
        data['assertion'] = message.text
    if assertion is False:
        await message.answer('Этого аргумента нет в базе данных. Добавить?',
                             reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))
        return await FSMAddAssertion.add_assertion.set()  # state: add_assertion
    await message.answer('Напишите контрагрументы к этому утверждению, по одному за раз:',
                         reply_markup=ReplyMarkups.create_rm(1, True, 'Отмена'))
    await FSMAddAssertion.facts_init.set()  # If the argument is in the database, switch to adding facts to this argument


async def add__assertion(message: Message, state: FSMContext):  # state: add_assertion
    if message.text == 'Добавить':
        await message.delete()
        async with state.proxy() as data:
            await add_to_table(table='assertions', column='assertion_name', value=data['assertion'])
            await message.answer('Аргумент был добавлен в базу данных')
            await message.answer('Напишите контрагрументы по одному за раз и нажмите Enter')
            await FSMAddAssertion.facts_init.set()
    else:
        await message.answer('Действие отменено')
        await state.finish()


async def facts_init(message: Message, state: FSMContext):  # state: facts_init
    if message.text == 'Отмена':
        await message.delete()
        await message.answer('Действие отменено')
        return await state.finish()
    async with state.proxy() as data:
        data['fact'] = message.text
    await message.answer(f'Подтвердите добавление контраргумента в базу данных:\n\n{message.text}',
                         reply_markup=ReplyMarkups.create_rm(2, True, 'Добавить', 'Отмена'))

    await FSMAddAssertion.add_facts.set()


async def add__facts(message: Message, state: FSMContext):  # state: add_facts
    # TODO: Should be a check if the fact exists in the database
    if message.text == 'Добавить':
        async with state.proxy() as data:
            await add_to_child_table(parent_table='assertions', parent_table_pk_column='assertion_id',
                                     parent_table_column='assertion_name', parent_table_value=data['assertion'],
                                     child_table='facts', child_table_column='fact_name',
                                     child_table_value=data['fact'])
            await message.answer('Факт был добавлен в базу данных.\n\nДобавьте следующий контрагргумент'
                                 ' или нажмите "Отмена"', reply_markup=ReplyMarkups.create_rm(2, True, 'Отмена'))
            await FSMAddAssertion.facts_init.set()
    else:
        await message.answer('Действие отменено')
        await state.finish()


def register_admin_handlers(dp: Dispatcher):
    dp.register_message_handler(admin_start, commands=["start"], state="*", is_su=True)
    # ------------------- PROMOTE TO ADMIN -------------------
    dp.register_callback_query_handler(add_new_admin, text='admin_promote_ib', state="*", is_su=True)
    dp.register_message_handler(new_admin_id, state=FSMAddAdmin.add_admin_id, is_su=True)
    dp.register_message_handler(new_admin_name, state=FSMAddAdmin.add_admin_name, is_su=True)
    dp.register_message_handler(new_admin_confirm, state=FSMAddAdmin.confirm, is_su=True)
    # --------------------- REMOVE ADMIN ---------------------
    dp.register_callback_query_handler(delete_admin_from_list, text='admin_remove_ib', state="*", is_su=True)
    dp.register_message_handler(delete_admin_id, state=FSMDeleteAdmin.delete_admin_id, is_su=True)
    dp.register_message_handler(delete_admin_confirm, state=FSMDeleteAdmin.confirm, is_su=True)
    # ------------------- SELECT ALL ADMINS ------------------
    dp.register_callback_query_handler(select_admins, text='admins_list_ib', state="*", is_su=True)
    # ------------------- LAST 10 FEEDBACKS ------------------
    dp.register_callback_query_handler(last_10_feedbacks, text='last_10_feedbacks_ib', state="*", is_su=True)
    # --------------------- ADD ASSERTION --------------------
    dp.register_callback_query_handler(assertion_init, text='add_section_ib', state="*", is_su=True)
    dp.register_message_handler(check_assertion, state=FSMAddAssertion.initialize, is_su=True)
    dp.register_message_handler(add__assertion, state=FSMAddAssertion.add_assertion, is_su=True)
    dp.register_message_handler(facts_init, state=FSMAddAssertion.facts_init, is_su=True)
    dp.register_message_handler(add__facts, state=FSMAddAssertion.add_facts, is_su=True)
