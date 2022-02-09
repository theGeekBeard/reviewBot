from aiogram import executor

from loader import dp
import middlewares, filters, handlers

from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    # Set default commands
    await set_default_commands(dispatcher)

    # Notifies about launch
    await on_startup_notify(dispatcher)


if __name__ == '__main__':
    from middlewares.throttling_middleware import ThrottlingMiddleware

    dp.middleware.setup(ThrottlingMiddleware())
    executor.start_polling(dp, on_startup=on_startup)
