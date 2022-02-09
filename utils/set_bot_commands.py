from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Start dialog"),
            types.BotCommand("help", "Show information"),
            types.BotCommand("menu", "Show menu")
        ]
    )
