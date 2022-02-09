from datetime import datetime

from aiogram import types



class Database:

    def __init__(self, con):
        self.db = con
        self.sql = self.db.cursor()

    # Setters

    async def add_new_user(self):
        with self.db:
            user = types.User.get_current()
            old_user = await self.get_user(user.id)
            if old_user:
                return False

            user_id = user.id
            username = user.username
            full_name = user.full_name
            date = datetime.now().date()

            self.sql.execute(
                f"INSERT INTO users (user_id, username, full_name, registr_date) VALUES({user_id}, '{username}',"
                f"'{full_name}', '{date}')")

    async def set_language(self, lang):
        with self.db:
            user = types.User.get_current()
            self.sql.execute(f"UPDATE users SET language = '{lang}' WHERE user_id = {user.id}")

    async def add_new_product(self, name, photo, price, category_name):
        with self.db:
            category_id = await self.get_category_id(category_name)
            self.sql.execute(f"INSERT INTO products (name, photo, price, category_id) "
                             f"VALUES('{name}', '{photo}', {price}, {category_id})")

    async def set_purchase(self, buyer_id, product_id, amount, bill_id):
        with self.db:
            self.sql.execute(
                f"INSERT INTO purchase (buyer_id, product_id, amount, bill_id) VALUES({buyer_id}, {product_id}, "
                f"{amount}, '{bill_id}')")

    async def confirm_purchase(self, timestamp, status, bill_id):
        with self.db:
            self.sql.execute(
                f"UPDATE purchase SET purchase_time='{timestamp}', purchase_status={status} WHERE bill_id='{bill_id}'")

    async def add_admin(self, user_id):
        with self.db:
            old_admin = self.get_admins(user_id)
            if old_admin:
                return False
            self.sql.execute(
                f"INSERT INTO admins (user_id) VALUES({user_id})")

    async def edit_product(self, product_id, change_type, value):
        with self.db:
            sql_request = "UPDATE products SET {change_type}='{value}' WHERE id={product_id}".format(
                change_type=change_type,
                value=value,
                product_id=product_id)

            self.sql.execute(sql_request)

    async def delete_product(self, product_id):
        with self.db:
            self.sql.execute(f"DELETE FROM products WHERE id={product_id}")

    # Getters

    async def get_user(self, user_id):
        self.sql.execute(f"SELECT * FROM users WHERE user_id = '{user_id}'")
        user = self.sql.fetchone()
        return user

    async def get_users(self):
        self.sql.execute(f"SELECT user_id FROM users")
        users = self.sql.fetchall()
        return users

    async def get_category_id(self, category_name):
        self.sql.execute(f"SELECT id FROM categories WHERE name = '{category_name}'")
        category_id = self.sql.fetchone()[0]
        return category_id

    async def get_all_products(self, category_name=False):
        if category_name:
            category_id = await self.get_category_id(category_name)
            self.sql.execute(f"SELECT id, name FROM products WHERE category_id = {category_id}")
        else:
            self.sql.execute(f"SELECT * FROM products")
        products = self.sql.fetchall()
        return products

    async def get_one_product(self, product_id):
        self.sql.execute(f"SELECT * FROM products WHERE id = {product_id}")
        product = self.sql.fetchone()
        return product

    async def get_purchase_history(self, user_id):
        self.sql.execute(f"SELECT purchase.purchase_time, products.name, products.photo, purchase.amount"
                         f" FROM purchase INNER JOIN products ON products.id = purchase.product_id"
                         f" WHERE purchase.buyer_id = {user_id} AND purchase.purchase_status = true")
        purchased_products = self.sql.fetchall()
        return purchased_products

    def get_admins(self, user_id=False):  # неасинхронная
        if user_id:
            self.sql.execute(f"SELECT user_id FROM admins WHERE user_id = {user_id}")
        else:
            self.sql.execute(f"SELECT user_id FROM admins")
        admins = self.sql.fetchall()
        return admins

    async def get_category_name_with_product(self, product_id):
        self.sql.execute(f"SELECT categories.name FROM categories INNER JOIN products ON categories.id = "
                         f"products.category_id WHERE products.id = {product_id}")
        return self.sql.fetchone()[0]

