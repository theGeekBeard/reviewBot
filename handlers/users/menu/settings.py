from typing import Union

from aiogram import types
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from handlers.users.commands.menu import show_menu
from handlers.users.other import send_application
from keyboards.inline.callback_data import language_cd, make_lang_cd
from loader import dp, _, db


@dp.message_handler(text=["⚙️Настройки", "⚙️Settings", "⚙️Налаштування"])
async def get_settings_info(message: Union[types.Message, CallbackQuery]):
    text = _("Раздел *Настройки*\n")

    settingsBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_('🏳️Изменить язык'), callback_data="change_lang"),
             InlineKeyboardButton(text=_('🌟Стать администратором'), callback_data="become_admin")]
        ]
    )

    if isinstance(message, types.Message):
        await message.answer(text, reply_markup=settingsBtn, parse_mode="Markdown")
    elif isinstance(message, CallbackQuery):
        call = message
        await call.message.edit_text(_(text), reply_markup=settingsBtn, parse_mode="Markdown")


@dp.callback_query_handler(text="change_lang")
async def change_language(call: Union[CallbackQuery, types.Message], isStart=False):
    langBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🇷🇺Русский',
                                  callback_data=make_lang_cd(language="RU", isStart=isStart))],
            [InlineKeyboardButton(text='🇬🇧󠁧󠁢󠁥󠁮󠁧󠁿English',
                                  callback_data=make_lang_cd(language="EN", isStart=isStart))],
            [InlineKeyboardButton(text='🇺🇦Український',
                                  callback_data=make_lang_cd(language="UK", isStart=isStart))]
        ]
    )

    if not isStart:
        langBtn.row(
            InlineKeyboardButton(text=_("🔙Назад"),
                                 callback_data=make_lang_cd(back="1", isStart=isStart)))

    if isinstance(call, types.Message):
        message = call
        await message.answer("🔻Выберите язык: \n\n🔻Select language:", reply_markup=langBtn)
    elif isinstance(call, CallbackQuery):
        await call.message.edit_text("🔻Выберите язык: \n\n🔻Select language:", reply_markup=langBtn)


@dp.callback_query_handler(language_cd.filter(back="1"))
async def come_back(call: CallbackQuery, callback_data):
    await get_settings_info(call)


@dp.callback_query_handler(language_cd.filter())
async def set_language(call: CallbackQuery, callback_data: dict):
    language = callback_data.get("language")

    await db.set_language(language)

    if callback_data["isStart"] == "True":
        await call.message.delete()
        await call.message.answer(_("<b>Добро пожаловать!</b>\n\n"
                                    "Это ReviewBot - бот, предназначенный для ознакомления с уровнем профессиональности "
                                    "разработки телеграм ботов. Бот реализован в виде простого интернет магазина с простыми "
                                    "товарами, которые действительно можно купить от 0 до 10 руб.\n\n"
                                    "<b>Внимание! Приобретение товаров нужно всего лишь для тестирования, никаких серьезных"
                                    " покупок и продаж здесь не существует!</b>\n\n"
                                    "Для ознакомления с дополнительной информацией перейдите в раздел <b>Помощь</b> из пункта "
                                    "меню, который появится после выбора языка."
                                    "\n\nДанного бота создал @theGeekBeard. Информацию о нем можно "
                                    "узнать в описании его профиля, а так же написав ему в личные сообщения",
                                    locale=language),
                                  parse_mode="HTML")
        await show_menu(call.message, locale=language)
    else:
        await call.message.edit_text(
            _("✅*Язык изменен*\n\nНажмите /menu, чтобы изменить язык кнопок меню", locale=language),
            reply_markup=None, parse_mode="Markdown")


@dp.callback_query_handler(text="become_admin")
async def set_admin(call: CallbackQuery):
    userId = call.message.chat.id

    admin = db.get_admins(user_id=userId)
    if admin:
        return await call.answer(_("🔴Вы уже администратор"))
    username = call.message.chat.username
    text = _("🔜...Ваша заявка отправлена администратору\n" \
             "Бот сообщит, когда заявка будет одобрена")

    await call.message.edit_text(text, reply_markup=None)

    await send_application(username, userId)
