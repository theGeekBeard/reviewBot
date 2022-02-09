from typing import Tuple, Any

from aiogram import types
from aiogram.contrib.middlewares.i18n import I18nMiddleware


async def get_lang(user_id):
    from loader import db

    user = await db.get_user(user_id)
    if user:
        return user[-2]


class ACLMiddleware(I18nMiddleware):
    async def get_user_locale(self, action: str, args: Tuple[Any]):
        user = types.User.get_current()
        return await get_lang(user.id) or user.locale


def setup_middleware(dp):
    from data.config import I18nDomain, LOCALES_DIR

    i18n = ACLMiddleware(I18nDomain, LOCALES_DIR)
    dp.middleware.setup(i18n)
    return i18n
