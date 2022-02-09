from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.inline.callback_data import new_admin_cd
from loader import dp, _, db, bot


@dp.callback_query_handler(text="cancel", state="*")
async def cancel_action(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(_("❌Действие отменено"))

    await state.finish()


@dp.callback_query_handler(new_admin_cd.filter())
async def add_new_admin(call: CallbackQuery, callback_data: dict):
    user_id = callback_data.get("user_id")

    if await db.add_admin(user_id) is None:
        text = "✅Ваша заявка на получение прав администратора одобрена!\n\n " \
               "Введите команду /help, чтобы посмотореть команды администатора\n\n" \
                "✅Your application for admin rights has been approved!\n\n " \
                "Type /help to see admin commands\n\n"
        await bot.send_message(user_id, text)
        await call.message.edit_text("✅Админ добавлен", reply_markup=None)


# for me (translation not need)
async def send_application(username, user_id):
    markup = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Добавить', callback_data=new_admin_cd.new(user_id=user_id))]
        ]
    )
    await bot.send_message(956405195, text=f"{username} хочет стать администратором"
                                           f"Добавить его?", reply_markup=markup)


async def get_cancel_btn():
    cancelBtn = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=_('❌Отмена'), callback_data='cancel')]
        ]
    )
    return cancelBtn