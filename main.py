from db_requests import db
import threading
from scheduler import Scheduler


def vk():
    # import vk
    pass


def tg():
    # import telegram_bot
    pass


# tg_thread = threading.Thread(target=tg)
# vk_thread = threading.Thread(target=vk)
# tg_thread.start()
# vk_thread.start()


# print('hello gays')
# print(get_categories())
# print(get_category('Напитки'))
# a = db.insert_order(1, '15.11.2023 6:51', 1, {"Кока-кола 0.5л в стекле": 2,
#                                            "Фанта 0.5л в стекле": 3})
# print(a)
db.del_item('Orders', 3)
with db.db as con:
    # pass
    print(con.execute('SELECT * FROM Orders').fetchall())
    print(con.execute('SELECT * FROM Order_lists').fetchall())


# print(get_client(123456789))
# print(get_client(123456788))

