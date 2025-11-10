from aiogram import types, Dispatcher, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from datetime import datetime

from fsm.order import CreateOrderFSM

from database import db

from config import settings

from google_sheets.api import cache_manager

from utils.logger import get_bot_logger


async def ask_name(c: types.CallbackQuery, state: FSMContext):
    # empty cart check

    cart = await db.get_user_cart(c.from_user.id)

    if cart:

        await state.set_state(CreateOrderFSM.name_state)
        await c.message.answer(
            "Введите своё имя"
        )
    
        await c.answer()
    else: 
        await c.answer(
            "Корзина пуста! Сначала добавьте в нее товары",
            show_alert=True
        )


async def ask_phone_number(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text.strip())
    await state.set_state(CreateOrderFSM.phone_number_state)

    phone_number_markup = types.ReplyKeyboardMarkup(
        keyboard=[
            [
                types.KeyboardButton(
                    text="Поделиться номером телефона",
                    request_contact=True
                )
            ]
        ],
        resize_keyboard=True
    )

    await m.answer(
        "Введите номер телефона или воспользуйтесь кнопкой автоматической отправки",
        reply_markup=phone_number_markup
    )


async def create_order(m: types.Message, state: FSMContext):
    s_data = await state.get_data()
    await state.clear()

    if m.contact:
        phone_number = m.contact.phone_number
    else:
        phone_number = m.text.strip()

    cart = await db.get_user_cart(m.from_user.id)

    now = datetime.now()

    offer = []

    message_to_admin = f"""
Новый заказ от пользователя:
Имя: {s_data['name']}
Телефон: {phone_number}
ID: {m.from_user.id}

Корзина:\n
"""

    for c in cart:
        offer.append(
            {
                "Дата и время": now,
                "Имя пользователя": s_data["name"],
                "ID пользователя": m.from_user.id,
                "Телефон": phone_number,
                "ID товара": c["good_id"],
                "Количество": c["number"]
            }
        )

        message_to_admin += f"{c['good_id']} - {c['number']} шт.\n"

    cache_manager.add_offers(
        offer
    )

    try:
        await m.bot.send_message(
            chat_id=settings.ORDERS_CHAT_ID,
            text=message_to_admin
        )
    except (TelegramForbiddenError, TelegramBadRequest):
        get_bot_logger().error("Не удалось отправить сообщение в чат заказов")

    await db.clear_user_cart(m.from_user.id)

    await m.answer(
        "Заказ успешно создан!"
    )


def register_offer_handlers(dp: Dispatcher):
    dp.callback_query.register(ask_name, F.data == "offer")
    dp.message.register(ask_phone_number, StateFilter(CreateOrderFSM.name_state))
    dp.message.register(create_order, StateFilter(CreateOrderFSM.phone_number_state))
