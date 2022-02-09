from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from handlers.users.other import get_cancel_btn
from keyboards.inline.callback_data import completed_cd, get_parameter_for_change_cd
from loader import ADMINS, _, db
from loader import dp
from states import states


@dp.message_handler(user_id=ADMINS, commands=["change_item"])
async def get_products_for_change(message: types.Message, state: FSMContext):
    from handlers.users.menu.products import get_product_categories
    await message.answer(_("*Режим администратора*:"), parse_mode="Markdown")
    await get_product_categories(message, state=state, isAdmin=True)


# buttons are in products.py
@dp.callback_query_handler(get_parameter_for_change_cd.filter())
async def define_change_type(call: CallbackQuery, callback_data: dict, state: FSMContext):
    productId = callback_data["product_id"]
    change_type = callback_data["change_type"]

    if change_type == "delete":
        await ask_complete_delete(call, productId, state)
    elif change_type == "change":
        await get_markup_for_edit(call, productId)


# Edit product
async def get_markup_for_edit(call: CallbackQuery, product_id):

    buttonsTexts = {
        1: _('📃Название'),
        2: _('💰Цена'),
        3: _('📷Фото')
    }

    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=buttonsTexts[1], callback_data=f"edit:name:{product_id}")],
            [InlineKeyboardButton(text=buttonsTexts[2], callback_data=f"edit:price:{product_id}")],
            [InlineKeyboardButton(text=buttonsTexts[3], callback_data=f"edit:photo:{product_id}")]
        ]
    )

    await call.message.edit_reply_markup()
    await call.message.answer(_("🔻Выберите, что хотите изменить:"), reply_markup=markup)


@dp.callback_query_handler(text_contains="edit")
async def require_value(call: CallbackQuery, state: FSMContext):
    data = call.data.split(":")

    parameterEdit = data[1]
    productId = data[2]

    async with state.proxy() as data:
        data['parameterEdit'] = parameterEdit
        data['productId'] = productId

    await call.message.edit_text(_("🔻Введите значение"), reply_markup=await get_cancel_btn())

    await states.ChangeItem.Value.set()


@dp.message_handler(state=states.ChangeItem.Value, content_types=[types.ContentType.PHOTO, types.ContentType.TEXT])
async def change_product(message: types.Message, state: FSMContext):
    if not message.photo:
        value = message.text
    else:
        value = message.photo[-1].file_id

    async with state.proxy() as data:
        parameterEdit = data['parameterEdit']
        productId = data['productId']

    await db.edit_product(productId, parameterEdit, value)

    await message.answer(_("✅<b>Товар успешно изменен</b>"), parse_mode="HTML")

    await state.finish()


# Delete product
async def ask_complete_delete(call: CallbackQuery, product_id, state: FSMContext):

    yesOrNoBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_('🆗Да'), callback_data="yes_or_no:yes"),
             InlineKeyboardButton(text=_('✖️Нет'), callback_data="yes_or_no:no")]
        ]
    )

    await call.message.edit_reply_markup()
    await call.message.answer(_("Вы уверены?"), reply_markup=yesOrNoBtn)

    async with state.proxy() as data:
        data['productId'] = product_id


@dp.callback_query_handler(completed_cd.filter())
async def delete_product(call: CallbackQuery, state: FSMContext, callback_data: dict):
    if callback_data["result"] == "yes":
        async with state.proxy() as data:
            productId = data['productId']

        await db.delete_product(productId)

        await call.message.edit_text(_("✅<b>Товар успешно удален</b>"), reply_markup=None, parse_mode="HTML")
    else:
        await call.message.edit_text(_("🚫<b>Действие отменено</b>"), reply_markup=None, parse_mode="HTML")
