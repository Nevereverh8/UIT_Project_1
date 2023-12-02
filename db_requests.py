import json
import sqlite3 as sl
import datetime as dt
with open('config.json') as file:
    db_path = json.load(file)['db_path']
    print('database connected to ' + db_path)
db = sl.connect(db_path, check_same_thread=False)
pending_orders = {}
if __name__ == '__main__':
    category_list = ['Напитки', 'Курица', 'Мясо', 'Рыба', 'Салаты', 'Алкогольные напитки',
                     'Пиццы', 'Соусы', 'Десерты', 'Роллы', 'Детское меню']
    food_list = [['Кока-кола 0.5л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.5л в стекле', 2.50, 0, 1, 5],
                 ['Фанта 0.5л в стекле', 2.50, 0, 1, 5], ['Фанта 1л', 3.50, 0, 1, 5],
                 ['Кока-кола 0.6л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.6л в стекле', 2.50, 0, 1, 5],
                 ['Фанта 0.6л в стекле', 2.50, 0, 1, 5], ['Фанта 1.1л', 3.50, 0, 1, 5],
                 ['Кока-кола 0.7л в стекле', 2.50, 0, 1, 5], ['Бонаква 0.7л в стекле', 2.50, 0, 1, 5],
                 ['Фанта 0.7л в стекле', 2.50, 0, 1, 5], ['Фанта 1.2л', 3.50, 0, 1, 5],
                 ['Куриные наггетсы 9 шт', 7.99, 0, 2, 20], ['Куриные наггетсы 15 шт', 10.49, 0, 2, 20],
                 ['Свинные отбивные 350 гр', 7.99, 0, 3, 25], ['Мясо по французски 350 гр', 9.99, 0, 3, 25],
                 ['Филе хека 300 гр', 9.34, 0, 4, 40], ['Запеченый лосось 500 г', 20.99, 0, 4, 50],
                 ['Мимоза 350 гр', 6.20, 0, 5, 20], ['Селедь под шубой 350 гр', 7.09, 0, 5, 20],
                 ['Пиво Stella Artois 350 гр', 5.20, 0, 6, 5], ['Вино Alazan Valley 350 гр', 5.20, 0, 6, 20],
                 ['Пицца 4 сыра 700 гр', 15.30, 0, 7, 30], ['Пицца маргарита 700 гр', 14.10, 0, 7, 30]]

    with db as con:
        # Orders
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Orders(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        client_id INTEGER,
                        time_placed TEXT,
                        delivery_time TEXT,
                        is_finished INTEGER,
                        is_aborted INTEGER,
                        admin_processed,
                        total_price REAL)
                        ''')
        # Order_lists
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Order_lists(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        food_id INTEGER,
                        amount float,
                        order_id INTEGER)
                        ''')

        # Food
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Food(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        price REAL,
                        stop_flag INTEGER,
                        category_id INTEGER,
                        cook_time INTEGER)
                        ''')
        sql_insert = '''INSERT INTO Food (name, price, stop_flag, category_id, cook_time) VALUES (?,?,?,?,?)'''
        for i in food_list:
            con.execute(sql_insert, i)

        # Categories
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Categories(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name TEXT)
                        ''')
        sql_insert = '''INSERT INTO Categories (name) VALUES (?)'''
        for i in category_list:
            con.execute(sql_insert, [i])

        # Admins
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Admins(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        role INTEGER,
                        tg_id INTEGER)
                        ''')
        sql_insert = '''INSERT INTO Admins (name, role, tg_id) VALUES (?,?,?)'''
        con.execute(sql_insert, ["Юра", 2, 413844851])
        con.execute(sql_insert, ["Костя", 2, 821927308])

        # Clients
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Clients(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        tel INTEGER,
                        adress TEXT,
                        chat_type TEXT,
                        chat_id INTEGER)
                        ''')
        sql_insert = '''INSERT INTO Clients (name, tel , adress, chat_type, chat_id) VALUES (?,?,?,?,?)'''
        con.execute(sql_insert, ['Женя', 375291234567, 'ул. Пушкина д.42 к.2, кв 69', 'VK', 123456789])
        # Food_reviews
        con.execute('''
                        CREATE TABLE IF NOT EXISTS Food_reviews(
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        food_id INTEGER,
                        client_id INTEGER,
                        rating INTEGER,
                        comment TEXT)
                        ''')


# further below there will be the most common requests
# to make it easier to implement this to bots

class DataBase:
    def __init__(self):
        global db
        self.db = db

    def get_categories(self):
        """
        Returns list of all categories
        """
        with self.db as con:
            categories = con.execute('''SELECT name FROM Categories''')
            categories = categories.fetchall()
            return [i[0] for i in categories]

    def get_category(self, category: str):
        """
        Returns dict of given category {name: price, ...}
        """
        with self.db as con:
            food = con.execute(f'''
                                         SELECT name, price FROM Food
                                         WHERE category_id = (SELECT id FROM Categories
                                                              WHERE name = "{category}"  AND stop_flag = 0)
                                         ''')
            food = food.fetchall()
            dict_of_food = {}
            for i in food:
                dict_of_food[i[0]] = i[1]
            return dict_of_food

    def insert_order(self, client_id: int, time_placed: str, admin_id: int, order_list: dict):
        """
        Inserts order and order list(shopping cart) to the database.
        time_placed is "DD.MM.YYYY HH:MM".

        :param order_list: dict {'name': 'amount', ...}
        :return: delivery time in minutes
        :rtype: int
        """
        with self.db as con:
            # add order with blank delivery time and total price
            sql_insert_order = '''INSERT INTO Orders (client_id, time_placed, delivery_time,
                                                      is_finished, is_aborted, admin_processed,
                                                      total_price)
                                  VALUES (?,?,?,?,?,?,?) '''
            con.execute(sql_insert_order, [client_id, time_placed, ' ', 0, 0, admin_id, 0])
            order_id = con.execute('SELECT max(id)  from Orders').fetchone()[0]

            # add cart into order list
            sql_insert_order_list = '''INSERT INTO Order_lists (food_id, amount, order_id)
                                  VALUES (?,?,?)'''
            total_price = 0
            for food, amount in order_list.items():
                food_id = con.execute(f'''SELECT id FROM Food
                                   WHERE name = '{food}' ''').fetchone()[0]
                price = con.execute(f'''SELECT price FROM Food
                               WHERE id = '{food_id}' ''').fetchone()[0]
                total_price += price * amount
                con.execute(sql_insert_order_list, [food_id, amount, order_id])

            # Update order with delivery time and tota price
            sql_update_order = f'''UPDATE Orders
                                  SET delivery_time = 30 + (SELECT MAX(cook_time) FROM Food
                                                       WHERE id IN (SELECT food_id FROM Order_lists
                                                                         WHERE order_id = '{order_id}'
                                                                         )
                                                            ),
                                      total_price = {total_price}
                                 WHERE id = {order_id}
                                   '''
            con.execute(sql_update_order)

            # return delivery time
            return con.execute(f'''SELECT delivery_time FROM Orders 
                           WHERE id = '{order_id}' 
                           ''').fetchone()[0]

    def get_client(self, client_chat_id: int):
        """
         Returns tuple of client data or None if there is no such.

        :return: (id, name, tel, age, adress, chat_type, chat_id) or None
        :param client_chat_id: id of client chat
        :rtype: tuple
        """
        with self.db as con:
            client = con.execute(f'''
                           SELECT * from Clients
                           WHERE chat_id = {client_chat_id}
            ''')
            client = client.fetchone()
            if client:
                return client
            else:
                return None

    def insert_client(self, name: str, tel: int, adress: str, chat_type: str, chat_id: int):
        """
        If client in database - retruns id, if not - adds and return id

        :param chat_type: VK or TG
        :return: id of inserted client
        :rtype: int
        """
        with self.db as con:
            a = con.execute(f'''
                                   SELECT * from Clients
                                   WHERE chat_id = {chat_id}
                    ''').fetchone()
            if a:
                client_id = a[0]
            else:
                con.execute(f'''INSERT INTO Clients (name, tel, adress, chat_type, chat_id)
                                  VALUES ('{name}', {tel}, '{adress}', '{chat_type}', {chat_id}) ''')
                client_id = con.execute('''SELECT max(id) FROM Clients''').fetchone()[0]
            return client_id

    def insert_admin(self, name: str, role: int, tg_id: int):
        """
        Inserts admin to database

        :param role: 1 or 2
        """
        with self.db as con:
            a = con.execute(f'''
                                   SELECT * from Admins
                                   WHERE tg_id = {tg_id}
                    ''').fetchone()
            if a:
                tg_id = a[0][2]
            else:
                con.execute(f'''INSERT INTO Clients (name, tel, age, adress, chat_type, chat_id)
                                  VALUES ('{name}', {role}, {tg_id}''')

    def del_admin(self, tg_id):
        with self.db as con:
            con.execute(f'''DELETE FROM Admins
                            WHERE tg_id = {tg_id}''')

    def stop_food(self, food_name):
        with self.db as con:
            con.execute(f'''UPDATE Food
                            SET stop_flag = 1 
                            WHERE name = '{food_name}' ''')

    def unstop_food(self, food_name):
        with self.db as con:
            con.execute(f'''UPDATE Food
                            SET stop_flag = 0 
                            WHERE name = '{food_name}' ''')

    def get_item(self, table: str,  value: any, by='id'):
        """
        Returns record from table by any given field (by id as default)

        :rtype: tuple
        """
        if type(value) == str:
            value = "'"+value+"'"
        with self.db as con:
            return con.execute(f'''SELECT * FROM {table}
                            WHERE {by} = {value}''').fetchall()

    def update_cell(self, table: str, id: int, param: str, value: any):
        """
        Sets parameter(param) of item(by id) in table(table) to (value)
        """
        if type(value) == str:
            value = "'"+value+"'"
        with self.db as con:
            con.execute(f'''UPDATE {table}
                            SET '{param}' = {value}
                            WHERE id = {id} ''')

    def del_item(self, table: str, id: int):
        """
        Deletes record from table by id
        """
        with self.db as con:
            con.execute(f'''DELETE FROM {table}
                            WHERE id = {id}''')

    def day_stat(self, date):
        day, month, year = date.split('.')
        with self.db as con:
            count = con.execute(f"""SELECT COUNT(id) FROM Orders
                                    WHERE time_placed LIKE '{day}.{month}.{year}%'
                                    """).fetchone()[0]
            delivered = con.execute(f"""SELECT COUNT(id) FROM Orders
                                        WHERE time_placed LIKE '{day}.{month}.{year}%' AND
                                              is_finished = 1
                                    """).fetchone()[0]
            aborted = con.execute(f"""SELECT COUNT(id) FROM Orders
                                        WHERE time_placed LIKE '{day}.{month}.{year}%' AND
                                              is_aborted = 1
                                    """).fetchone()[0]
        return f"Ordered at this day:{count}\nDelivered at this day:{delivered}\nAborted orders at this day:{aborted}"

    def week_stat(self, date):
        day, month, year = date.split('.')
        week = dt.date(int(year), int(month), int(day)).isocalendar().week
        week = [dt.date.fromisocalendar(int(year), week, i) for i in range(1, 8)]
        dates = [f'{i.day}.{i.month}.{i.year}' for i in week]
        cond_list = ''
        for i in dates:
            cond_list += f"time_placed LIKE '{i.split('.')[0]}.{i.split('.')[1]}.{i.split('.')[2]}%' AND "
        cond_list = cond_list[:-5]
        with self.db as con:
                count = con.execute(f"""SELECT COUNT(id) FROM Orders
                                                   WHERE time_placed LIKE {cond_list}
                                                   """).fetchone()[0]
                delivered = con.execute(f"""SELECT COUNT(id) FROM Orders
                                                       WHERE time_placed LIKE {cond_list} AND
                                                             is_finished = 1
                                                   """).fetchone()[0]
                aborted = con.execute(f"""SELECT COUNT(id) FROM Orders
                                                       WHERE time_placed LIKE {cond_list} AND
                                                             is_aborted = 1
                                                   """).fetchone()[0]
        return f"Ordered at this week:{count}\nDelivered at this week:{delivered}\nAborted orders at this week:{aborted}"


db = DataBase()