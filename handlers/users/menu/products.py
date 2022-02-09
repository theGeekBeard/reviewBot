from datetime import datetime
from typing import Union

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import payment_cd, product_cd, make_prod_cd
from loader import dp, _, db, bot
from payments import qiwi


async def product_menu_navigation(level, call, callback_data, state):
    levels = {
        0: get_product_categories,
        1: get_product_names,
        2: get_info_one_product,
        3: get_purchase_info
    }

    navigation_function = levels[int(level) - 1]

    await navigation_function(call, callback_data=callback_data, state=state)


# back = "1" - means the back button is pressed
@dp.callback_query_handler(product_cd.filter(back="1"))
async def come_back(call: CallbackQuery, callback_data: dict, state: FSMContext):
    await product_menu_navigation(callback_data["level"], call, callback_data, state)


@dp.message_handler(text=["📦Товары", "📦Products", "📦Товари"])
async def get_product_categories(message: Union[types.Message, CallbackQuery], state: FSMContext,
                                 callback_data: dict = False, isAdmin=False):
    async with state.proxy() as data:
        data['isAdmin'] = isAdmin

    productsCategoriesBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("👔Одежда"),
                                  callback_data=make_prod_cd(level="0", category="👔Одежда")),
             InlineKeyboardButton(text=_('🖥Электроника'),
                                  callback_data=make_prod_cd(level="0", category="🖥Электроника")),
             InlineKeyboardButton(text=_('🏚Для дома'),
                                  callback_data=make_prod_cd(level="0", category="🏚Для дома"))]
        ]
    )

    # the level value is stored in the button file itself
    if isinstance(message, types.Message):
        await message.answer(_("*Категории товаров:*"), reply_markup=productsCategoriesBtn, parse_mode="Markdown")
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.delete()
        await call.message.answer(_("*Категории товаров:*"), reply_markup=productsCategoriesBtn, parse_mode="Markdown")


@dp.callback_query_handler(product_cd.filter(level="0"))
async def get_product_names(call: CallbackQuery, state: FSMContext, callback_data: dict):
    LEVEL = "1"

    categoryName = callback_data["category_name"]

    text = _("<b>Категория:</b>") + " <i>" + _(str(categoryName)) + "</i>"

    products = await db.get_all_products(categoryName)

    prodMarkup = InlineKeyboardMarkup()

    for product in products:
        productId = product[0]
        name = product[1]

        prodMarkup.insert(InlineKeyboardButton(text=name, callback_data=make_prod_cd(
            level=LEVEL, category=categoryName, prod_id=productId
        )))

    prodMarkup.row(
        InlineKeyboardButton(text=_("🔙Назад"), callback_data=make_prod_cd(level=LEVEL, back="1")))

    await call.message.delete()
    await call.message.answer(text, reply_markup=prodMarkup, parse_mode="HTML")


@dp.callback_query_handler(product_cd.filter(level="1"))
async def get_info_one_product(call: CallbackQuery, callback_data: dict, state: FSMContext):
    LEVEL = "2"

    async with state.proxy() as data:
        isAdmin = data['isAdmin']

    productId = callback_data.get("product_id")

    productData = await db.get_one_product(productId)
    categoryName = await db.get_category_name_with_product(productId)

    productName = productData[1]
    productPhoto = productData[2]
    productPrice = productData[3]

    caption = f"{productName}: {productPrice}₽"

    if isAdmin:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=_("✏️Изменить"), callback_data=f"change_product:change:{productId}")],
                [InlineKeyboardButton(text=_("🗑Удалить"), callback_data=f"change_product:delete:{productId}")]
            ]
        )

    else:
        markup = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=_("💵Купить"), callback_data=make_prod_cd(level=LEVEL, prod_id=productId,
                                                                                     price=productPrice,
                                                                                     category=categoryName)
                                      )]
            ]
        )

    markup.row(
        InlineKeyboardButton(text=_("🔙Назад"),
                             callback_data=make_prod_cd(level=LEVEL, back="1", category=categoryName)))

    await call.message.delete()
    await call.message.answer_photo(productPhoto, caption=caption, reply_markup=markup)


@dp.callback_query_handler(product_cd.filter(level="2"))
async def get_purchase_info(call: CallbackQuery, callback_data: dict, state: FSMContext):
    LEVEL = "3"

    productId = callback_data.get("product_id")
    price = callback_data.get("product_price")

    bill = await qiwi.generate_payment_form(price)
    await db.set_purchase(call.message.chat.id, productId, price, bill.bill_id)

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("↗️Перейти к оплате"), url=bill.pay_url)],
            [InlineKeyboardButton(text=_("✔️Проверить оплату"), callback_data=payment_cd.new(bill_id=bill.bill_id))]
        ]
    )

    markup.row(
        InlineKeyboardButton(text=_("🔙Назад"), callback_data=make_prod_cd(level=LEVEL, back="1",
                                                                           prod_id=productId)))

    await call.message.edit_reply_markup(markup)


@dp.callback_query_handler(payment_cd.filter())
async def check_payment(call: CallbackQuery, callback_data: dict, state: FSMContext):
    bill_id = callback_data.get("bill_id")

    if await qiwi.check_payment(bill_id):
        time = datetime.now()
        await db.confirm_purchase(timestamp=time, status=True, bill_id=bill_id)

        await call.message.edit_reply_markup()
        await call.message.answer(_("<b>✅Оплата прошла успешно!</b>"), parse_mode="HTML")
    else:
        await call.answer(_("❌Товар не оплачен"))
