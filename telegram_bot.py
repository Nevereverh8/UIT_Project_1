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
def gen_foods(food, chat_id, temp=0):
    dish = f'{food[0]} цена за шт. - {food[1]}'
    if dish in sessions[chat_id]['cart']:
        temp = sessions[chat_id]['cart'][dish]
    keyb_food = InlineKeyboardMarkup()
    keyb_food.add(InlineKeyboardButton('-', callback_data=f'fa;{food[0]};-'), InlineKeyboardButton(f'Кол-во: {temp}', callback_data='None'),InlineKeyboardButton('+', callback_data=f'fa;{food[0]};+'))
    keyb_food.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'f;{food[0]};{temp}')) #Добавить в calldatу кол-во товара, из кнопки кол-во
    return keyb_food
   
# Отдельный слайдер для блюд в категории
# Unique slider for dishes in categories
def gen_slider(page, fix_pos=1):
    start = fix_pos*(page-1)
    end = start + fix_pos
    keyb_slider = InlineKeyboardMarkup()
    keyb_slider.add(InlineKeyboardButton('Назад', callback_data=f'fn-back-{page}'), InlineKeyboardButton('Корзина', callback_data='cart'), InlineKeyboardButton('Вперед', callback_data=f'fn-forward-{page}'))
    keyb_slider.add(InlineKeyboardButton('Вернуться в меню', callback_data='m'))
    return keyb_slider, start, end, page

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == '/start':
        sessions[message.chat.id] = {}
        sessions[message.chat.id]['last_foods'] = {}
        sessions[message.chat.id]['cart'] = {}
        sessions[message.chat.id]['food_list'] = []
        sessions[message.chat.id]['real_cart'] = {}
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
#       fn-forward-'page' - next page
#       fn-back-'page' - previus page

@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    bot.answer_callback_query(callback_query_id=call.id)
    if call.data == 'm':
        # Удаляет сообщения возвращая пользователя в меню
        # Delete message returning the user to menu
        if sessions[call.message.chat.id]['last_foods'] != {}:
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            for item in sessions[call.message.chat.id]['last_foods']:
                bot.delete_message(chat_id=call.message.chat.id, message_id=item)
            sessions[call.message.chat.id]['last_foods'] = {}
        else:
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
        sessions[call.message.chat.id]['food_list'] = db.get_category(call.data.split('-')[1])
        slider = gen_slider(1)
        food_list = sessions[call.message.chat.id]['food_list']
        for f in list(food_list.keys())[slider[1]:slider[2]]:
            a = bot.send_message(call.message.chat.id, f'{f} цена за шт. - {food_list[f]}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id, 0))
            sessions[call.message.chat.id]['last_foods'][a.message_id] = 0
        bot.send_message(call.message.chat.id, 'Навигация', reply_markup=slider[0])

    # Callback для кнопок + и -. UPD 02:1 18.11
    # Callback buttons + and -, I tend to think that it is shit code
    if call.data.split(';')[0] == 'fa':
        if call.data.split(';')[2] == '+':
            if call.message.text in sessions[call.message.chat.id]['cart']:
                sessions[call.message.chat.id]['cart'][call.message.text] += 1
            else:
                sessions[call.message.chat.id]['cart'][call.message.text] = 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['cart'][call.message.text]))
        if call.data.split(';')[2] == '-':
            if call.message.text in sessions[call.message.chat.id]['cart']:
                sessions[call.message.chat.id]['cart'][call.message.text] -= 1
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['cart'][call.message.text]))
                if sessions[call.message.chat.id]['cart'][call.message.text] == 0:
                    sessions[call.message.chat.id]['cart'].pop(call.message.text)
           

    # Переключение страниц блюд в категории с помощью слайдера
    # Switching dishes pages in categories with help of slider
    if call.data.split('-')[0] == 'fn':
        if call.data.split('-')[1] == 'forward':
            slider = gen_slider(int(call.data.split('-')[2])+1)
            food_list = sessions[call.message.chat.id]['food_list']
            for f in list(food_list.keys())[slider[1]:slider[2]]:
                for id in sessions[call.message.chat.id]['last_foods']: 
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=id, text=f'{f} цена за шт. - {food_list[f]}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id)) 
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Навигация', reply_markup=gen_slider(slider[3])[0])
                    break
        if call.data.split('-')[1] == 'back':
            slider = gen_slider(int(call.data.split('-')[2])-1)
            food_list = sessions[call.message.chat.id]['food_list']
            for f in list(food_list.keys())[slider[1]:slider[2]]:
                for id in sessions[call.message.chat.id]['last_foods']:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=id, text=f'{f} цена за шт. - {food_list[f]}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id)) 
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Навигация', reply_markup=gen_slider(slider[3])[0])
                    break
    if call.data.split(';')[0] == 'f':
        sessions[call.message.chat.id]['real_cart'][call.message.text] = call.data.split(';')[2]
        print(sessions[call.message.chat.id]['real_cart'])
        sys.stdout.flush() 
    
    if call.data == 'cart':
        with open(r'photos\amogus.jpg', 'rb') as f:
           a = bot.send_photo(call.message.chat.id, f, 'amogus')
           print(a.photo[0].file_id)
           sys.stdout.flush()
        bot.edit_message_caption('amogud edited', call.message.chat.id, a.message_id)

           
# Надо добавить корзину.
# Need to add cart

print("Ready")

bot.infinity_polling()    

