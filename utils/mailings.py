from loader import db, _, bot


async def send_products_to_users(text, photo):
    users = await db.get_users()

    caption = _("<b>Новый товар!</b>") + "\n\n" + text

    for user_id in users:
        await bot.send_photo(photo=photo, caption=caption, chat_id=user_id[0], parse_mode="HTML")


