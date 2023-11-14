import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import *

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns');

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        a = get_categories()
        print(a)
        bot.send_message(message.chat.id,"Тут будет инфа о ресторане!")

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    
print("Ready")

bot.infinity_polling()    

