import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import *
import sys

# sys.stdout.flush() После принта

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns')

keyb_menu = InlineKeyboardMarkup()
keyb_menu.add(InlineKeyboardButton('Меню', callback_data='m-1'))

# Генерирует 1-ую страницу меню
# Gen 1-st menu page
def gen_menu(page):
    categories, keyb_categories = get_categories(), InlineKeyboardMarkup()
    start = page-1 + 4*(page-1)
    end = start + 5
    print(categories,'\n',start, end)
    sys.stdout.flush()
    for c in categories[start:end]:
        keyb_categories.add(InlineKeyboardButton(c, callback_data=f'c-{c}'))
    if end > 5:
        keyb_categories.add(InlineKeyboardButton('Назад', callback_data='c-back'))
    if 10 <= end < len(categories):
        keyb_categories.add(InlineKeyboardButton('Впред', callback_data='c-forward')) 
    return keyb_categories

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        bot.send_message(message.chat.id, """Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана. Все вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню.""", reply_markup=keyb_menu)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == 'm-1':
        bot.send_message(call.message.chat.id, "Меню", reply_markup=gen_menu(2))
print("Ready")

bot.infinity_polling()    

