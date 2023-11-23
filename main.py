from db_requests import db
import threading
import time
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


# # # down here is the test area

# db.del_item('Orders', 3)
# with db.db as con:
#     # pass
#     print(con.execute('SELECT * FROM Orders').fetchall())
#     print(con.execute('SELECT * FROM Order_lists').fetchall())

schedule = Scheduler()
print(f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}")


def daily_stat():
    today_date = f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}"
    print(db.stat(today_date))

daily_stat()
# print(get_client(123456789))
# print(get_client(123456788))


