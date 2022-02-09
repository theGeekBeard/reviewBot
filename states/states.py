from aiogram.dispatcher.filters.state import StatesGroup, State


class Product(StatesGroup):
    name = State()
    photo = State()
    price = State()
    confirm = State()


class Purchase(StatesGroup):
    Quantity = State()


class ChangeItem(StatesGroup):
    Value = State()


