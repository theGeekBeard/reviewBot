import random

from aiogram import types
from pyqiwip2p import QiwiP2P

from data.config import QIWI_TOKEN

p2p = QiwiP2P(auth_key=QIWI_TOKEN)


async def generate_payment_form(price):
    userId = types.User.get_current().id

    comment = f"{userId} {random.randint(1000, 10001)}"
    bill = p2p.bill(amount=price, lifetime=10, comment=comment)

    return bill


async def check_payment(bill_id):
    if str(p2p.check(bill_id=bill_id).status) == "PAID":
        return True
    return False
