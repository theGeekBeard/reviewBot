from aiogram import types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from loader import dp, _


@dp.message_handler(commands=["menu"])
async def show_menu(message: types.Message, locale=None):
    menuKeyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=_('👤Профиль', locale=locale)),
             KeyboardButton(text=_('📦Товары', locale=locale))],
            [KeyboardButton(text=_('🆘Помощь', locale=locale)),
             KeyboardButton(text=_('⚙️Настройки', locale=locale))]
        ],
        resize_keyboard=True
    )

    await message.answer(_("*Главное меню:*", locale=locale), reply_markup=menuKeyboard, parse_mode="Markdown")
