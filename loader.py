import psycopg2
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import DATABASE, USER, PASSWORD, HOST
from database import Database
from middlewares.language_middleware import setup_middleware

from data import config

bot = Bot(token=config.BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

i18n = setup_middleware(dp)

_ = i18n.gettext

con = psycopg2.connect(dbname=DATABASE, user=USER, password=PASSWORD, host=HOST)
db = Database(con)

admins = db.get_admins()
ADMINS = [x[0] for x in admins]  # Тут у нас будет список из админов
