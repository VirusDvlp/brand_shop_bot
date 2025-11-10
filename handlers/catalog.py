from aiogram import types, Dispatcher, F
from aiogram.enums import ParseMode

from markups.market import get_brand_list_markup, get_market_markup

from google_sheets.data_reader import cached_data_reader

from database import db

from text import get_good_card_text



def get_good_card_in_catalog(category: int, page: int = 0):
    category_goods = cached_data_reader.get_all_records(category)

    good = None
    if category_goods:
        try:
            good = category_goods[page]
        except IndexError:
            good = category_goods[-1]

    return {
        "good": good,
        "total_pages": len(category_goods),
        "is_to_right": page + 1 < len(category_goods),
        "is_to_left": page > 0
    }


def get_google_drive_url(url: str) -> str:
    if url:
        if not url.startswith('http'):
            url = 'https://' + url
        
        if '/d/' in url:
            start_index = url.find('/d/') + 3
            end_index = url.find('/', start_index)
            if end_index == -1:
                end_index = url.find('?', start_index)
            if end_index == -1:
                file_id = url[start_index:]
            else:
                file_id = url[start_index:end_index]
            
            # Создаем прямую ссылку для скачивания
            return f"https://drive.google.com/uc?export=download&id={file_id}"
        
    return "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSvHdRZDerGbZ57-ps_PwHdfI90X4p1sr8I4w&s"


async def send_brand_list(c: types.CallbackQuery):
    await c.answer()

    await c.message.answer(
        "Выберите бренд",
        reply_markup=await get_brand_list_markup()
    )


async def send_first_brand_good(c: types.CallbackQuery):
    brand = int(c.data.split('_')[1])

    goods_data = get_good_card_in_catalog(
        brand
    )

    if goods_data:

        count_in_cart = await db.count_goods_in_cart(
            c.from_user.id,
            goods_data["good"]["ID"],
            brand
        )

        await c.message.answer_photo(
            photo=types.URLInputFile(get_google_drive_url(goods_data["good"]["Фото"])),
            caption=get_good_card_text(
                name=goods_data["good"]["Название"],
                descr=goods_data["good"]["Описание"],
                usage=goods_data["good"]["Показания к применению"],
                volume=goods_data["good"]["Объем"],
                price=goods_data["good"]["Цена"]
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=get_market_markup(
                goods_data["is_to_right"],
                goods_data["is_to_left"],
                0,
                goods_data["total_pages"],
                goods_data["good"]["ID"],
                brand,
                count_in_cart if count_in_cart else 0

            ),
        )
    else:
        await c.message.answer(
            "Не найдено товаров данного бренда"
        )

    await c.answer()


async def catalog_right(c: types.CallbackQuery):
    a, page, brand = c.data.split('_')
    page = int(page)
    brand = int(brand)

    goods_data = get_good_card_in_catalog(brand, page + 1)

    if goods_data:

        count_in_cart = await db.count_goods_in_cart(
            c.from_user.id,
            goods_data["good"]["ID"],
            brand
        )
        await c.message.edit_media(
            media=types.InputMediaPhoto(media=get_google_drive_url(goods_data["good"]["Фото"])),
        )
        await c.message.edit_caption(
            caption=get_good_card_text(
                name=goods_data["good"]["Название"],
                descr=goods_data["good"]["Описание"],
                usage=goods_data["good"]["Показания к применению"],
                volume=goods_data["good"]["Показания к применению"],
                price=goods_data["good"]["Цена"]
            ),
            parse_mode=ParseMode.HTML
        )
        await c.message.edit_reply_markup(
            reply_markup=get_market_markup(
                goods_data["is_to_right"],
                goods_data["is_to_left"],
                page + 1,
                goods_data["total_pages"],
                goods_data["good"]["ID"],
                brand,
                count_in_cart if count_in_cart else 0
            ),
        )
    else:
        await c.message.answer(
            "Не найдено товаров данного бренда"
        )

    await c.answer()


async def catalog_left(c: types.CallbackQuery):
    a, page, brand = c.data.split('_')
    page = int(page)
    brand = int(brand)

    goods_data = get_good_card_in_catalog(brand, page - 1)

    if goods_data:
        count_in_cart = await db.count_goods_in_cart(
            c.from_user.id,
            goods_data["good"]["ID"],
            brand
        )

        await c.message.edit_media(
            media=types.InputMediaPhoto(media=get_google_drive_url(goods_data["good"]["Фото"])),
        )
        await c.message.edit_caption(
            caption=get_good_card_text(
                name=goods_data["good"]["Название"],
                descr=goods_data["good"]["Описание"],
                usage=goods_data["good"]["Показания к применению"],
                volume=goods_data["good"]["Показания к применению"],
                price=goods_data["good"]["Цена"]
            ),
            parse_mode=ParseMode.HTML
        )
        await c.message.edit_reply_markup(
            reply_markup=get_market_markup(
                goods_data["is_to_right"],
                goods_data["is_to_left"],
                page - 1,
                goods_data["total_pages"],
                goods_data["good"]["ID"],
                brand,
                count_in_cart if count_in_cart else 0

            ),
        )
    else:
        await c.message.edit_text(
            "Не найдено товаров данного бренда"
        )


async def add_to_cart(c: types.CallbackQuery):
    a, good, brand, page = c.data.split('_')

    await db.add_good_to_cart(c.from_user.id, good, int(brand))

    goods_data = get_good_card_in_catalog(int(brand), int(page) + 1)

    if goods_data:
        count_in_cart = await db.count_goods_in_cart(
            c.from_user.id,
            goods_data["good"]["ID"],
            int(brand)
        )
        await c.message.edit_media(
            media=types.InputMediaPhoto(media=get_google_drive_url(goods_data["good"]["Фото"])),
        )
        await c.message.edit_caption(
            caption=get_good_card_text(
                name=goods_data["good"]["Название"],
                descr=goods_data["good"]["Описание"],
                usage=goods_data["good"]["Показания к применению"],
                volume=goods_data["good"]["Показания к применению"],
                price=goods_data["good"]["Цена"]
            ),
            parse_mode=ParseMode.HTML
        )
        await c.message.edit_reply_markup(
            reply_markup=get_market_markup(
                goods_data["is_to_right"],
                goods_data["is_to_left"],
                int(page),
                goods_data["total_pages"],
                goods_data["good"]["ID"],
                brand,
                count_in_cart if count_in_cart else 0

            ),
        )
    else:
        await c.message.edit_text(
            "Не найдено товаров данного бренда"
        )





async def delete_from_cart(c: types.CallbackQuery):
    a, good, brand, page = c.data.split('_')

    await db.delete_from_cart(c.from_user.id, good, int(brand))

    goods_data = get_good_card_in_catalog(int(brand), int(page) + 1)

    if goods_data:
        count_in_cart = await db.count_goods_in_cart(
            c.from_user.id,
            goods_data["good"]["ID"],
            brand
        )
        await c.message.edit_media(
            media=types.InputMediaPhoto(media=get_google_drive_url(goods_data["good"]["Фото"])),
        )
        await c.message.edit_caption(
            caption=get_good_card_text(
                name=goods_data["good"]["Название"],
                descr=goods_data["good"]["Описание"],
                usage=goods_data["good"]["Показания к применению"],
                volume=goods_data["good"]["Показания к применению"],
                price=goods_data["good"]["Цена"]
            ),
            parse_mode=ParseMode.HTML
        )
        await c.message.edit_reply_markup(
            reply_markup=get_market_markup(
                goods_data["is_to_right"],
                goods_data["is_to_left"],
                int(page),
                goods_data["total_pages"],
                goods_data["good"]["ID"],
                brand,
                count_in_cart if count_in_cart else 0

            ),
        )
    else:
        await c.message.edit_text(
            "Не найдено товаров данного бренда"
        )


def register_catalog_handlers(dp: Dispatcher):
    dp.callback_query.register(send_brand_list, F.data == "catalog")
    dp.callback_query.register(send_first_brand_good, F.data.startswith("brand_"))
    dp.callback_query.register(catalog_left, F.data.startswith("catalogleft_"))
    dp.callback_query.register(catalog_right, F.data.startswith("catalogright_"))
    dp.callback_query.register(add_to_cart, F.data.startswith("cartadd_"))
    dp.callback_query.register(delete_from_cart, F.data.startswith("cartdel_"))
