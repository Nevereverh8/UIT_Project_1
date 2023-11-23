import schedule
from db_requests import db
import threading
import time
import datetime as dt

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


print(f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}")


def daily_stat():
    today_date = f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}"
    print(db.day_stat(today_date))


def weekly_stat():
    today_date = f"{time.localtime().tm_mday}.{time.localtime().tm_mon}.{time.localtime().tm_year}"
    print(db.week_stat(today_date))


schedule.every().day.at('23:59').do(daily_stat)
schedule.every().sunday.at('23:59').do(weekly_stat)
while True:
    schedule.run_pending()
    time.sleep(1)
# print(get_client(123456789))
# print(get_client(123456788))


