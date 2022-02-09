from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, _


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    text = _("<b>📋Список команд:</b> \n\n"
             "/start - Начать диалог \n"
             "/help - Получить справку\n"
             "/menu - Отобразить кнопки меню\n\n"
             "<b>🌟Для администраторов:</b>\n\n"
             "/add_item - Добавить новый товар\n"
             "/change_item - Изменить товар")

    await message.answer(text, parse_mode="HTML")
