from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import sheet_categories


brand_list_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text=sheet_categories[i], callback_data=f"brand_{i}")
            
        ]
        for i in range(len(sheet_categories))
    ]
)

brand_list_markup.inline_keyboard.extend(
    [
        [
            InlineKeyboardButton(text="Задать вопрос", callback_data="question")
        ],
        [
            InlineKeyboardButton(text="Как заказать?", callback_data="instruction")
        ]
    ]
)


def get_market_markup(
    is_to_right: bool, is_to_left: bool, page: int, total_pages: int, good_id, brand, in_cart_count
):



    inline_keyboard=[]

    paging = []

    if is_to_left:
        paging.append(
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"catalogleft_{page}_{brand}"
            )
        )

    paging.append(
        InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data=" "
        )
    )

    if is_to_right:
        paging.append(
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"catalogright_{page}_{brand}"
            )
        )

    inline_keyboard.append(paging)

    inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Заказать",
                callback_data="offer"
            )
        ]
    )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text="Корзина", callback_data="open_cart"),
            InlineKeyboardButton(
                text="◀️",
                callback_data=f"cartdel_{good_id}_{brand}_{page}"
            ),
            InlineKeyboardButton(
                text=str(in_cart_count),
                callback_data=" ",
            ),
            InlineKeyboardButton(
                text="▶️",
                callback_data=f"cartadd_{good_id}_{brand}_{page}"
            )
        ]
    )

    inline_keyboard.append(
        [
            InlineKeyboardButton(text="В начало", callback_data=" ")
        ]
    )


    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )


def get_cart_markup(cart: list):
    inline_keyboard = []

    if cart:
        for c in cart:
            inline_keyboard.extend(
                [
                    [
                        InlineKeyboardButton(text=c['name'], callback_data=' '),
                        InlineKeyboardButton(text='❌', callback_data=f'killcart_{c["id"]}')
                    ]
                ]
            )
        inline_keyboard.append(
            [
                InlineKeyboardButton(text="Оформить заказ", callback_data="offer"),
                InlineKeyboardButton(text="Очистить", callback_data="clear_cart")
            ]
        )
    
    inline_keyboard.append(
        [InlineKeyboardButton(text="В начало", callback_data="start")]
    )

    return InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )
