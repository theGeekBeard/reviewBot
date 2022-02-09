from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from loader import dp, _


@dp.message_handler(text=["🆘Помощь", "🆘Help", "🆘Допомога"])
async def get_help(message: types.Message):
    text = _("🆘Раздел <b>Помощь</b>\n\n"
             "1. Как стать администратором? - В разделе <i>Настройки</i>\n"
             "2. Замена языка - В разделе <i>Настройки</i>\n"
             "3. Просмотр купленных товаров - В разделе <i>Профиль</i>\n"
             "4. Команды администратора - Команда /help")

    helpBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_('✉️Связаться с менеджером'), url="https://t.me/theGeekBeard")]
        ]
    )

    await message.answer(text, reply_markup=helpBtn, parse_mode="HTML")
