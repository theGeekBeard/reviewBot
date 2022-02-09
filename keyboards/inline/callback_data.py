from aiogram.utils.callback_data import CallbackData

categories_admin_cd = CallbackData("show_admin_categories", "category_name")
categories_cd = CallbackData("show_categories", "category_name")
buy_cd = CallbackData("set_buy", "product_id")
payment_cd = CallbackData("payment", "bill_id")
new_admin_cd = CallbackData("new_admin", "user_id")
change_product_cd = CallbackData("change_product", "change_type", "product_id")
completed_cd = CallbackData("yes_or_no", "result")
get_parameter_for_change_cd = CallbackData("change_product", "change_type", "product_id")

product_cd = CallbackData("prod_all", "level", "category_name", "product_id", "product_price", "back")
language_cd = CallbackData("set_language", "language", "back", "isStart")


def make_prod_cd(level, category="0", prod_id="0", price="0", back="0"):
    return product_cd.new(level=level, category_name=category, product_id=prod_id, product_price=price, back=back)


def make_lang_cd(language="0", back="0", isStart="False"):
    return language_cd.new(language=language, back=back, isStart=isStart)
