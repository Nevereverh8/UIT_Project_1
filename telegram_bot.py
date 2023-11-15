import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import *
import sys

# sys.stdout.flush() После принта

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns')

sessions = {}

keyb_menu = InlineKeyboardMarkup()
keyb_menu.add(InlineKeyboardButton('Меню', callback_data='m-1'))

# Генерирует 1-ую страницу меню
# Gen 1-st menu page
def gen_menu(page):
    categories, keyb_categories = get_categories(), InlineKeyboardMarkup()
    # Расчет старта и конца для страницы
    # Calculation of the beginning and end of the page
    start = page-1 + 9*(page-1)
    end = start + 10
    for c in categories[start:end]:
        keyb_categories.add(InlineKeyboardButton(c, callback_data=f'c-{c}'))
    if end > 10:
        keyb_categories.add(InlineKeyboardButton('Назад', callback_data=f'c-back-{page}'))
    if 10 <= end < len(categories):
        keyb_categories.add(InlineKeyboardButton('Впред', callback_data=f'c-forward-{page}')) 
    return keyb_categories, page

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        sessions[message.chat.id] = {}
        bot.send_message(message.chat.id, """Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана. Все вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню.""", reply_markup=keyb_menu)

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == 'm-1':
        a = bot.send_message(call.message.chat.id, "Меню", reply_markup=gen_menu(2)[0])
        sessions[call.message.chat.id]['last_message'] = a.message_id

    # Cлайдер листает странцы
    # Slider to change pages
    if call.data.split('-')[0] == 'c':
        print(sessions, call.message.chat.id)
        sys.stdout.flush()
        if call.data.split('-')[1] == 'back':
            gen_menu_info = gen_menu(int(call.data.split('-')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]-1)[0])
        if call.data.split('-')[1] == 'forward':
            gen_menu_info = gen_menu(int(call.data.split('-')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]+1)[0])
print("Ready")

bot.infinity_polling()    

