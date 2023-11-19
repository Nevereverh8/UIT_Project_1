import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import db
import sys

# sys.stdout.flush() После принта

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns')

sessions = {}

keyb_menu = InlineKeyboardMarkup()
keyb_menu.add(InlineKeyboardButton('Меню', callback_data='m'))

# Генерирует 1-ую страницу меню
# Gen 1-st menu page
def gen_menu(page, fix_pos=10):
    categories, keyb_categories = db.get_categories(), InlineKeyboardMarkup()
    # Расчет старта и конца для страницы
    # Calculation of the beginning and end of the page
    print(categories)
    sys.stdout.flush()
    start = fix_pos*(page-1)
    end = start + fix_pos
    for c in categories[start:end]:
        keyb_categories.add(InlineKeyboardButton(c, callback_data=f'c-{c}'))
    if end > fix_pos:
        keyb_categories.add(InlineKeyboardButton('Назад', callback_data=f'cn-back-{page}'))
    if fix_pos <= end < len(categories):
        keyb_categories.add(InlineKeyboardButton('Впред', callback_data=f'cn-forward-{page}')) 
    return keyb_categories, page

# Генерирует позиции в котегории ps без слайдера
# Gen food in category
def gen_foods(food, call_message, temp=0):
    # это проверка чтоб в словаре было фиксированное 
    # кол-во айдишников блюд чтобы начать работу с кнопками + и -. 
    # Но пока это херня полная.
    # 
    # this checks dict for fixed amount of dishes id, 
    # to start working with plus and minus button correctly.
    # But my code is still bullshit 
    if len(sessions[call_message.chat.id]['last_foods']) < 2:
        temp = 0
    else:
        temp = sessions[call_message.chat.id]['last_foods'][call_message.message_id]
    keyb_food = InlineKeyboardMarkup()
    keyb_food.add(InlineKeyboardButton('-', callback_data=f'fa;{food[0]};-'), InlineKeyboardButton(f'Кол-во: {temp}', callback_data='None'),InlineKeyboardButton('+', callback_data=f'fa;{food[0]};+'))
    keyb_food.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'f;{food[0]};')) #Добавить в calldatу кол-во товара, из кнопки кол-во
    return keyb_food
   
# not ready yet, just preparation for next day
def gen_slider(page):
    keyb_slider = InlineKeyboardMarkup()
    keyb_slider.add(InlineKeyboardButton('Назад', callback_data=f'fn-back-{page}'), InlineKeyboardButton('Вперед', callback_data=f'fn-forward-{page}'))
    keyb_slider.add(InlineKeyboardButton('Вырнуться в меню', callback_data='m'))
    return keyb_slider

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        sessions[message.chat.id] = {}
        sessions[message.chat.id]['last_foods'] = {}
        sessions[message.chat.id]['cart'] = {}
        bot.send_message(message.chat.id, """Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана. Все вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню.""", reply_markup=keyb_menu)

# call back types: can be changed
#   m - menu
#   cn - category navigation
#       cn_back - back button
#       cn_forward - forward button
#   c - chosen category
#   f - chosen food 
#       fa;..;- - amount -1
#       fa;..;+ - amount +1

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == 'm':
        a = bot.send_message(call.message.chat.id, "Меню", reply_markup=gen_menu(1)[0])
        sessions[call.message.chat.id]['last_message_menu'] = a.message_id

    # Cлайдер листает странцы
    # Slider to change pages
    if call.data.split('-')[0] == 'cn':
        print(sessions, call.message.chat.id)
        sys.stdout.flush()
        if call.data.split('-')[1] == 'back':
            gen_menu_info = gen_menu(int(call.data.split('-')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message_menu'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]-1)[0])
        if call.data.split('-')[1] == 'forward':
            gen_menu_info = gen_menu(int(call.data.split('-')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message_menu'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]+1)[0])
    
    # Позиции в категории
    # Food in category
    if call.data.split('-')[0] == 'c':
        food_list = db.get_category(call.data.split('-')[1])
        for f in food_list:
            a = bot.send_message(call.message.chat.id, f'{f[0]} цена за шт. - {f[1]}', reply_markup=gen_foods(f, call.message, 0))
            sessions[call.message.chat.id]['last_foods'][a.message_id] = 0
        bot.send_message(call.message.chat.id, 'Навигация', reply_markup=gen_slider(1))

    # Callback для кнопок + и -. UPD 02:1 18.11
    # Callback buttons + and -, I tend to think that it is shit code
    if call.data.split(';')[0] == 'fa':
        if call.data.split(';')[2] == '+':
            sessions[call.message.chat.id]['last_foods'][call.message.message_id] += 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message, sessions[call.message.chat.id]['last_foods'][call.message.message_id]))
        if call.data.split(';')[2] == '-':
            if sessions[call.message.chat.id]['last_foods'][call.message.message_id] != 0:
                sessions[call.message.chat.id]['last_foods'][call.message.message_id] -= 1
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message, sessions[call.message.chat.id]['last_foods'][call.message.message_id]))
        print(sessions[call.message.chat.id])
        sys.stdout.flush()     

# Надо добавить навигацию и корзину.
# Need to add navigation slider and cart

print("Ready")

bot.infinity_polling()    

