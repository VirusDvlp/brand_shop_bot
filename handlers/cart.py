from aiogram import types, Dispatcher, F

from markups.market import get_cart_markup

from database import db
from google_sheets.data_reader import cached_data_reader


async def make_cart_info(user_id):
    def get_good_price(good_price, number):
        try:
            return int(good_price) * number
        except ValueError:
            return good_price
    user_cart = await db.get_user_cart(user_id)

    message_text = """
Ваша корзина:

"""

    if user_cart:
        i = 1
        total = 0
        cart_for_markup = []
        for c in user_cart:
            good_info = cached_data_reader.get_record(c["brand"], c["good_id"])

            if good_info:
                message_text += f"""
{i}. {good_info['Название']}
Количество: {c['number']}
Цента за шт: {good_info['Цена']}
Сумма: {get_good_price(good_info['Цена'], c['number'])}
"""
                try:
                    total += c['number'] * int(good_info['Цена'])
                except ValueError:
                    pass
                i += 1
                cart_for_markup.append(
                    {
                        "id": c['good_id'],
                        "brand": c['brand'],
                        "name": good_info["Название"]
                    }
                )

        return {
            "text": message_text,
            "markup": get_cart_markup(cart_for_markup)
        }
    else:
        return {
            "text": "В корзине пусто",
            "markup": get_cart_markup([])
        }


async def send_cart(c: types.CallbackQuery):
    
    cart_info = await make_cart_info(c.from_user.id)

    await c.message.answer(
        cart_info['text'],
        reply_markup=cart_info['markup']
    )
    await c.answer()




async def kill_position(c: types.CallbackQuery):
    good_id = c.data.split('_')[1]

    await db.delete_good_from_cart(c.from_user.id, good_id)

    cart_info = await make_cart_info(c.from_user.id)

    await c.message.edit_text(
        text=cart_info['text'],
    )

    await c.message.edit_reply_markup(
        reply_markup=cart_info['markup']
    )
    

    await c.answer()


async def clear_cart(c: types.CallbackQuery):

    await db.clear_user_cart(c.from_user.id)

    cart_info = await make_cart_info(c.from_user.id)

    await c.message.edit_text(
        text=cart_info['text'],
    )

    await c.message.edit_reply_markup(
        reply_markup=cart_info['markup']
    )
    
    

    await c.answer()


def register_cart_handlers(dp: Dispatcher):
    dp.callback_query.register(send_cart, F.data == "open_cart")
    dp.callback_query.register(kill_position, F.data.startswith("killcart_"))
    dp.callback_query.register(clear_cart, F.data == "clear_cart")
