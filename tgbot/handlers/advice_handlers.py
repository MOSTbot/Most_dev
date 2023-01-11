from __future__ import annotations

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from tgbot.kb import ReplyMarkups, InlineMarkups
from tgbot.utils import SQLRequests, SectionName


def register_advice_handlers(dp: Dispatcher) -> None:
    dp.register_callback_query_handler(advice_mode, text='adv_mode_start', state=None)
    dp.register_message_handler(advice_mode, commands=["advice"], state=None)
    dp.register_message_handler(advice_mode, Text(equals='🧠 Психология разговора', ignore_case=True), state=None)
    dp.register_callback_query_handler(advice_mode2,
                                       lambda call: call.data in SQLRequests
                                       .select_by_table_and_column('adv_assertions', 'topic_name'), state=None)
    dp.register_message_handler(advice_mode3,
                                lambda message: message.text in SQLRequests
                                .select_by_table_and_column('adv_answers', 'adv_answers'), state=None)


async def advice_mode(message: Message | CallbackQuery) -> None:
    SectionName.s_name = 'Психология разговора'  # for logging purposes
    if isinstance(message, CallbackQuery):
        message = message.message
    await  message.answer_photo(
        photo=open('tgbot/assets/advice.jpg', 'rb'),
        caption='🟢 Собрали советы психологов о том, как не сойти с ума и говорить о войне с близкими,'
                ' чего ожидать, как реагировать и вести себя.', reply_markup=ReplyKeyboardRemove())
    await  message.answer('❓ Почему важно говорить с близкими на сложные темы\n\n'
                          'В основе близких отношений лежит доверие. Оно разрушается, когда возникают темы, '
                          'которые надо обходить стороной — например, война. Разговор об этом может привести '
                          'к конфликтам, многие его избегают. Но на самоконтроль и попытки обходить вопрос '
                          'войны тратится много энергии: вы можете не замечать, как исчезает искренность, '
                          'растет внутреннее напряжение и вы отдаляетесь друг от друга.\n\n'
                          'В разговоре на сложную тему важно не ранить собеседника и помнить, '
                          'что даже болезненный разговор — это шаг навстречу. '
                          'Для этого есть техника безопасного общения, именно о ней мы рассказываем в этом разделе.\n\n'
                          'Выберите тему, чтобы прочитать ⬇',
                          reply_markup=InlineMarkups
                          .create_im(1, [*SQLRequests.
                                     select_by_table_and_column('adv_assertions', 'topic_name'), 'Главное меню'],
                                     [*SQLRequests.
                                     select_by_table_and_column('adv_assertions', 'topic_name'), 'main_menu']))
    await message.delete()


async def advice_mode2(call: CallbackQuery) -> None:
    adv_id = SQLRequests.select_by_table_and_column('adv_assertions', 'adv_id', 'topic_name', call.data)
    section_description = SQLRequests.select_by_table_and_column('adv_assertions', 'adv_description', 'topic_name', call.data)
    await call.answer(cache_time=10)
    await call.message.answer(*section_description, reply_markup=ReplyMarkups.create_rm(2, False,
                                            *SQLRequests.select_by_table_and_column('adv_answers', 'adv_answers', 'adv_id', *adv_id)))


async def advice_mode3(message: Message) -> None:
    await  message.answer(
        *SQLRequests.select_by_table_and_column('adv_answers', 'adv_description', 'adv_answers', message.text),
        reply_markup=InlineMarkups.create_im(1, ['Вернуться назад'], ['adv_mode_start']))
