from aiogram import types
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, _, db


@dp.message_handler(text=["👤Профиль", "👤Profile", "👤Профіль"])
async def get_profile_info(message: types.Message):
    profileBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_('👤Личные данные'), callback_data='personal_data'),
             InlineKeyboardButton(text=_('📜История покупок'), callback_data='purchase_history')]
        ]
    )

    text = _("Раздел *Профиль* \n"
             "Здесь вы можете просмотреть информацию о себе и историю ваших покупок")
    await message.answer(text, reply_markup=profileBtn, parse_mode="Markdown")


@dp.callback_query_handler(text_contains="personal_data")
async def get_personal_data(call: CallbackQuery):
    data = await db.get_user(call.message.chat.id)

    username = data[2]
    full_name = data[3]
    registrationDate = data[-1].strftime("%d-%m-%Y")

    text = _("👤<b>Ваши данные:</b>\n\n") + \
           _("Имя пользователя: ") + " <i>" + username + "</i>\n" + \
           _("Имя: ") + " <i>" + full_name + "</i>\n" + \
           _("Дата регистрации: ") + "<i>" + registrationDate + "</i>"

    await call.message.edit_text(text, parse_mode="HTML", reply_markup=None)


@dp.callback_query_handler(text="purchase_history")
async def get_purchase_history(call: CallbackQuery):
    await call.message.edit_text(_("📦*Ваша история покупок:*"), parse_mode="Markdown")

    purchaseHistory = await db.get_purchase_history(call.message.chat.id)

    if not purchaseHistory:
        return await call.message.answer(_("🔴У вас нет совершенных покупок, или купленный вами продукт удалили"))

    for product in purchaseHistory:
        text = _("📃<b>Товар:</b> ") + " <i>" + product[1] + "</i>\n" + \
               _("💰<b>Стоимость:</b> ") + " <i>" + str(product[-1]) + "</i>\n" + \
               _("📅<b>Дата покупки:</b> ") + " <i>" + product[0].strftime("%d-%m-%Y %H:%M") + "</i>"

        await call.message.answer_photo(photo=product[2], caption=text, parse_mode="HTML")
