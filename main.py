import runpy

import schedule
from db_requests import db
import threading
import time
from telegram_bot import pending_orders
import datetime as dt
import runpy
def vk():
    runpy.run_module('telegram_bot', {}, "__main__")


def tg():
    import vk_bot


tg_thread = threading.Thread(target=tg)
vk_thread = threading.Thread(target=vk)
tg_thread.start()
vk_thread.start()


# # # down here is the test area

# db.del_item('Orders', 3)
# with db.db as con:
#     # pass
#     print(con.execute('SELECT * FROM Orders').fetchall())
#     print(con.execute('SELECT * FROM Order_lists').fetchall())


#print(f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}")


def daily_stat():
    today_date = f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}"
    print(db.day_stat(today_date))


def weekly_stat():
    today_date = f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}"
    print(db.week_stat(today_date))


schedule.every().day.at('23:59').do(daily_stat)
schedule.every().sunday.at('23:59').do(weekly_stat)
print(db.insert_order(1, '12:40', 1, {'Кока-кола 0.5л в стекле': 2}))

print(str(time.localtime().tm_hour)+':'+str(time.localtime().tm_min))
while True:
    schedule.run_pending()
    print(pending_orders)
    time.sleep(5)
# print(get_client(123456789))
# print(get_client(123456788))


