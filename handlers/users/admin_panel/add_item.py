from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from handlers.users.other import get_cancel_btn
from loader import ADMINS
from keyboards.inline.callback_data import categories_admin_cd
from loader import dp, _, db, bot
from states import states
from utils.mailings import send_products_to_users


@dp.message_handler(user_id=ADMINS, commands=["add_item"])
async def get_category_list(message: types.Message):
    productsCategoriesAdminBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_("👔Одежда"),
                                  callback_data=categories_admin_cd.new(category_name='👔Одежда')),
             InlineKeyboardButton(text=_('🖥Электроника'),
                                  callback_data=categories_admin_cd.new(category_name='🖥Электроника')),
             InlineKeyboardButton(text=_('🏚Для дома'),
                                  callback_data=categories_admin_cd.new(category_name='🏚Для дома'))]
        ]
    )

    await message.answer(_("🔻Выберите <i>категорию</i>, куда вы хотите добавить новый товар:"),
                         reply_markup=productsCategoriesAdminBtn, parse_mode="HTML")


@dp.callback_query_handler(categories_admin_cd.filter())
async def ask_product_name(call: CallbackQuery, state: FSMContext, callback_data: dict):
    categoryName = callback_data.get("category_name")

    async with state.proxy() as data:
        data['categoryName'] = categoryName
        data['message_id'] = call.message.message_id

    text = _("<b>Вы выбрали категорию:</b> ") + " <i>" + _(str(categoryName)) + "</i>\n\n" + \
           _("🔻Теперь введите <i>название товара</i>, который хотите добавить")

    await call.message.edit_text(text, reply_markup=await get_cancel_btn(), parse_mode="HTML")

    await states.Product.name.set()


@dp.message_handler(state=states.Product.name)
async def ask_product_photo(message: types.Message, state: FSMContext):
    productName = message.text

    async with state.proxy() as data:
        categoryName = data['categoryName']
        messageId = data['message_id']
        data['productName'] = productName
        data['message_id'] = message.message_id + 1

    text = _("🗂<b>Категория товара:</b> ") + " <i>" + _(str(categoryName)) + "</i>\n" + \
           _("📃<b>Название товара:</b> ") + " <i>" + str(productName) + "</i>\n\n" + \
           _("🔻Пришлите мне <i>фотографию</i> товара или нажмите кнопку отмены")

    await bot.edit_message_reply_markup(message.chat.id, messageId, reply_markup=None)
    await message.answer(text, reply_markup=await get_cancel_btn(), parse_mode="HTML")

    await states.Product.photo.set()


@dp.message_handler(state=states.Product.photo, content_types=types.ContentType.PHOTO)
async def ask_product_price(message: types.Message, state: FSMContext):
    productPhoto = message.photo[-1].file_id

    async with state.proxy() as data:
        categoryName = data['categoryName']
        productName = data['productName']
        messageId = data['message_id']
        data['productPhoto'] = productPhoto
        data['message_id'] = message.message_id + 1

    text = _("🗂<b>Категория товара:</b> ") + " <i>" + _(str(categoryName)) + "</i>\n" + \
           _("📃<b>Название товара:</b> ") + " <i>" + str(productName) + "</i>\n\n" + \
           _("🔻Пришлите мне <i>стоимость</i> товара в рублях(₽) или нажмите кнопку отмены")

    await bot.edit_message_reply_markup(message.chat.id, messageId, reply_markup="")

    await message.answer_photo(photo=productPhoto, caption=text, reply_markup=await get_cancel_btn(), parse_mode="HTML")

    await states.Product.price.set()


@dp.message_handler(state=states.Product.price)
async def confirm_adding_product(message: types.Message, state: FSMContext):
    try:
        price = int(message.text)

        async with state.proxy() as data:
            categoryName = data['categoryName']
            productName = data['productName']
            productPhoto = data['productPhoto']
            messageId = data['message_id']
            data['price'] = price

        await bot.edit_message_reply_markup(message.chat.id, message_id=messageId, reply_markup='')
    except ValueError:
        text = _("❌Вы ввели неверное значение, введите число")
        await message.answer(text)
        return

    text = _("🗂<b>Категория товара:</b> ") + " <i>" + _(str(categoryName)) + "</i>\n" + \
           _("📃<b>Название товара:</b> ") + " <i>" + productName + "</i>\n" + \
           _("💰<b>Стоимость товара:</b> ") + " <i>" + str(price) + "</i>\n\n" + \
           _("🔻Добавить товар?")

    markup = await get_cancel_btn()
    markup.add(InlineKeyboardButton(text=_("Добавить"), callback_data='add'))
    await message.answer_photo(photo=productPhoto, caption=text, reply_markup=markup, parse_mode="HTML")

    await states.Product.confirm.set()


@dp.callback_query_handler(text="add", state=states.Product.confirm)
async def add_product(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        categoryName = data['categoryName']
        productName = data['productName']
        productPhoto = data['productPhoto']
        productPrice = data['price']

    await db.add_new_product(productName, productPhoto, productPrice, categoryName)

    await call.message.delete()

    text = _("🗂<b>Категория товара:</b> ") + " <i>" + _(str(categoryName)) + "</i>\n" + \
           _("📃<b>Название товара:</b> ") + " <i>" + productName + "</i>\n" + \
           _("💰<b>Стоимость товара:</b> ") + " <i>" + str(productPrice) + "</i>\n\n"

    await call.message.answer_photo(photo=productPhoto, caption=text + _("✅<b>Товар успешно создан</b>"),
                                    parse_mode="HTML")

    await send_products_to_users(text, productPhoto)

    await state.reset_state()
