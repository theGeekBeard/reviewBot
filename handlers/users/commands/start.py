from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from handlers.users.menu.settings import change_language
from loader import dp, db, _


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await message.answer("<b>Добро пожаловать!</b>\n\n<b>Welcome!</b>", parse_mode="HTML")
    await db.add_new_user()
    await change_language(message, isStart=True)
