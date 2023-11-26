import time

import telebot
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from db_requests import db
import sys

# sys.stdout.flush() После принта

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns')
admin_chat_id = -1002019810166

sessions = {}
admin_session = {}
pending_orders = {}

keyb_menu = InlineKeyboardMarkup()
keyb_menu.add(InlineKeyboardButton('Меню', callback_data='m;m'))

key_order = InlineKeyboardMarkup()
key_order.add(InlineKeyboardButton('Изменить заказ', callback_data='cart;0'), InlineKeyboardButton('Продолжить', callback_data='o;next'))

keyb_order_card = InlineKeyboardMarkup()
keyb_order_card.add(InlineKeyboardButton('Изменить заказ', callback_data='cart;0'))

keyb_finish = InlineKeyboardMarkup()
keyb_finish.add(InlineKeyboardButton('Изменить заказ', callback_data='cart;0'), InlineKeyboardButton('Изменить адрес доставки', callback_data='o;o'),  InlineKeyboardButton('Меню', callback_data='m;m'))
keyb_finish.add(InlineKeyboardButton('Оформить заказ', callback_data='o;send'))

keyb_panel = InlineKeyboardMarkup()
keyb_panel.add(InlineKeyboardButton('Изменение базы', callback_data='adm;db'), InlineKeyboardButton('Изменение администраторов', callback_data='adm;adm'))

keyb_admin_management = InlineKeyboardMarkup()
keyb_admin_management.add(InlineKeyboardButton('Добавить админа', callback_data='adm;ad'))
keyb_admin_management.add(InlineKeyboardButton('Изменить уровень админа', callback_data='adm;ed'))
keyb_admin_management.add(InlineKeyboardButton('Удалить админа', callback_data='adm;del'))
keyb_admin_management.add(InlineKeyboardButton('Назад', callback_data='adm;back'))

keyb_db_change = InlineKeyboardMarkup()
keyb_db_change.add(InlineKeyboardButton('Поствить товар на стоп', callback_data='db;change'))
keyb_db_change.add(InlineKeyboardButton('Назад', callback_data='adm;back'))

def admin_management(call_data):
    keyb_yes_back = InlineKeyboardMarkup()
    if call_data == 'ad':
        callback = 'add;yes'
        button_text = 'Добавить'
    elif call_data == 'del':
        callback = 'del;yes'
        button_text = 'Удалить'
    elif call_data == 'ed':
        callback = 'edit;yes'
        button_text = 'Изменить'
    keyb_yes_back.add(InlineKeyboardButton('Назад', callback_data='adm;adm'), InlineKeyboardButton(button_text, callback_data=callback))
    
    return keyb_yes_back 

# Генерирует 1-ую страницу меню
# Gen 1-st menu page
def gen_menu(page, fix_pos=10, callback = ('c', 'cn')):
    categories, keyb_categories = db.get_categories(), InlineKeyboardMarkup()
    # Расчет старта и конца для страницы
    # Calculation of the beginning and end of the page
    print(categories)
    sys.stdout.flush()
    start = fix_pos*(page-1)
    end = start + fix_pos
    for c in categories[start:end]:
        keyb_categories.add(InlineKeyboardButton(c, callback_data=f'{callback[0]};{c}'))
    if end > fix_pos:
        keyb_categories.add(InlineKeyboardButton('Назад', callback_data=f'{callback[1]};back;{page}'))
    if fix_pos <= end < len(categories):
        keyb_categories.add(InlineKeyboardButton('Впред', callback_data=f'{callback[1]};forward;{page}')) 
    if callback[0] == 'db':
        keyb_categories.add(InlineKeyboardButton('Вернуться', callback_data='panel;0'))
    return keyb_categories, page

# Генерирует позиции в котегории ps без слайдера
# Gen food in category
def gen_foods(food, chat_id, temp=0, name='foods'):
    dish = f'{food[0]} цена за шт. - {food[1]}'
    keyb_food = InlineKeyboardMarkup()
    if name == 'foods':
        if dish in sessions[chat_id]['cart']:
            temp = sessions[chat_id]['cart'][dish]
        keyb_food.add(InlineKeyboardButton('-', callback_data=f'fa;-'), InlineKeyboardButton(f'Кол-во: {temp}', callback_data='None'),InlineKeyboardButton('+', callback_data=f'fa;+'))
        keyb_food.add(InlineKeyboardButton('Добавить в корзину', callback_data=f'f;{temp}')) #Добавить в calldatу кол-во товара, из кнопки кол-во
    elif name == 'cart':
        temp = sessions[chat_id]['real_cart'][food]
        keyb_food.add(InlineKeyboardButton('-', callback_data=f'crta;-'), InlineKeyboardButton(f'Кол-во: {temp}', callback_data=temp),InlineKeyboardButton('+', callback_data=f'crta;+'))
    elif name == 'db_change':
        print(db.get_item('Food', food[0], 'name'))
        keyb_food.add(InlineKeyboardButton('Убрать товар из меню', callback_data='db;stop'))
    return keyb_food
    
# Отдельный слайдер для блюд в категории
# Unique slider for dishes in categories
def gen_slider(page, fix_pos=2, name = 'foods', cal = any):
    start = fix_pos*(page-1)
    end = start + fix_pos
    if name == 'foods':
        keyb_slider = InlineKeyboardMarkup()
        keyb_slider.add(InlineKeyboardButton('Назад', callback_data=f'fn;back;{page}'), InlineKeyboardButton('Ваш заказ', callback_data='o;o'), InlineKeyboardButton('Вперед', callback_data=f'fn;forward;{page}'))
        keyb_slider.add(InlineKeyboardButton('Вернуться в меню', callback_data='m;m'))
    elif name == 'cart':
        keyb_slider = InlineKeyboardMarkup()
        keyb_slider.add(InlineKeyboardButton('Назад', callback_data=f'crt;back;{page}'), InlineKeyboardButton('Вперед', callback_data=f'crt;forward;{page}'))
        keyb_slider.add(InlineKeyboardButton('Вернуться в меню', callback_data='m;c'))
        if sessions[cal]['real_cart']:
            keyb_slider.add(InlineKeyboardButton('Оформить заказ', callback_data=f'o;o'))
    elif name == 'db_change':
        keyb_slider = InlineKeyboardMarkup()
        keyb_slider.add(InlineKeyboardButton('Назад', callback_data=f'dbf;back;{page}'), InlineKeyboardButton('Вперед', callback_data=f'dbf;forward;{page}'))
        keyb_slider.add(InlineKeyboardButton('Вернуться', callback_data='panel;0'))
         
    return keyb_slider, start, end, page

# Отправка заказа админам
def send_order(client_chat_type:str, client_chat_id:int, adress:str, tel:int, message_id, cart:dict):
    text, food_list = '', ''
    pending_orders[client_chat_type+str(client_chat_id)] = {}
    pending_orders[client_chat_type+str(client_chat_id)]['cart'] = cart
    pending_orders[client_chat_type+str(client_chat_id)]['adress'] = adress
    pending_orders[client_chat_type+str(client_chat_id)]['tel'] = tel
    pending_orders[client_chat_type+str(client_chat_id)]['message_id'] = message_id
    total_sum = 0
    for food, amount in cart.items():
        price = db.get_item('Food', food, 'name')[0][2]
        food_list += f"{food} * {amount} шт. = {price}\n"
        total_sum += price * amount
    text = f'Заказ из {client_chat_type} клиента {client_chat_id}\n\n'
    text += food_list+'Сумма заказа: '+str(total_sum) + ' руб.'

    i_kb = InlineKeyboardMarkup()
    i_kb.add(InlineKeyboardButton('Подтвердить', callback_data=f'adm;apr;{client_chat_type}{str(client_chat_id)}'),
             InlineKeyboardButton('X Вне зоны охвата', callback_data=f'adm;deca;{client_chat_type}{str(client_chat_id)}'),
             InlineKeyboardButton('X Неправильные данные', callback_data=f'adm;deco;{client_chat_type}{str(client_chat_id)}'))
    a = bot.send_message(admin_chat_id, text, reply_markup=i_kb)
    pending_orders[client_chat_type+str(client_chat_id)]['admin_message_id'] = a.message_id


@bot.message_handler(content_types=['text'])
def start(message):
    if message.chat.id != admin_chat_id and message.chat.id not in admin_session:
        if message.text == '/start':
            sessions[message.chat.id] = {}
            sessions[message.chat.id]['last_foods'] = {}
            sessions[message.chat.id]['cart'] = {}
            sessions[message.chat.id]['food_list'] = [] #Удалить потом
            sessions[message.chat.id]['real_cart'] = {}
            sessions[message.chat.id]['cart_ids'] = []
            sessions[message.chat.id]['adress_info'] = {}
            bot.send_message(message.chat.id, """Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана. Все вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню.""", reply_markup=keyb_menu)
        else:
            sessions[message.chat.id]['adress_info']['adress'] =\
                '\n'.join(sessions[message.chat.id]['adress_info']['adress'].split('\n')[:-1]) + \
                '\n'+"Ваш адрес: " + message.text    # message.text - Адрес
            bot.edit_message_text(chat_id=message.chat.id, message_id=sessions[message.chat.id]['adress_info']['id'],
                                  text=sessions[message.chat.id]['adress_info']['adress'],
                                  reply_markup=keyb_finish)
            if not message.from_user.is_bot:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    else:
        if message.text == '/panel':
            if message.from_user.id == db.get_item('Admins', message.from_user.id, 'tg_id')[0][3]:
                admin_session[message.from_user.id] = {}
                admin_session[message.from_user.id]['last_foods'] = []
                # admin_session[message.from_user.id] = message.chat
                # print(message)
                # sys.stdout.flush()
            bot.send_message(chat_id=message.from_user.id, text = 'Панель управления', reply_markup=keyb_panel) 
            bot.delete_message(chat_id=admin_chat_id, message_id=message.message_id)
        else:
            if message.from_user.is_bot == False:
                admin_session[message.from_user.id]['admin_to_change'] = message.text
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                bot.edit_message_text(chat_id=message.chat.id, message_id=admin_session[message.from_user.id]['action_id'][0], text=f"{admin_session[message.from_user.id]['last_message']} {message.text}", reply_markup=admin_management(admin_session[message.from_user.id]['action_id'][1]))

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
    print(call.data)
    # who pressed button = call.from_user['id']
    sys.stdout.flush()
    if call.data.split(';')[0] == 'm':
        # Удаляет сообщения возвращая пользователя в меню
        # Delete message returning the user to menu
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        
        if call.data.split(';')[1] == 'm':
            if sessions[call.message.chat.id]['last_foods'] != {}:
                for item in sessions[call.message.chat.id]['last_foods']:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=item)
                sessions[call.message.chat.id]['last_foods'] = {}
        if call.data.split(';')[1] == 'c':
            if sessions[call.message.chat.id]['cart_ids']:
                for item in sessions[call.message.chat.id]['cart_ids']:
                    bot.delete_message(chat_id=call.message.chat.id, message_id=item)
                sessions[call.message.chat.id]['cart_ids'] = []
        a = bot.send_message(call.message.chat.id, "Меню", reply_markup=gen_menu(1)[0])
        sessions[call.message.chat.id]['last_message_menu'] = a.message_id
        
    # Cлайдер листает странцы
    # Slider to change pages
    if call.data.split(';')[0] == 'cn':
        print(sessions, call.message.chat.id)
        sys.stdout.flush()
        if call.data.split(';')[1] == 'back':
            gen_menu_info = gen_menu(int(call.data.split(';')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message_menu'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]-1)[0])
        if call.data.split(';')[1] == 'forward':
            gen_menu_info = gen_menu(int(call.data.split(';')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['last_message_menu'], text="Меню", reply_markup=gen_menu(gen_menu_info[1]+1)[0])
    
    # Позиции в категории
    # Food in category
    if call.data.split(';')[0] == 'c':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        for id in sessions[call.message.chat.id]['last_foods']:
            bot.delete_message(chat_id=call.message.chat.id, message_id=id)
        sessions[call.message.chat.id]['food_list'] = db.get_category(call.data.split(';')[1])
        slider = gen_slider(1)
        food_list = sessions[call.message.chat.id]['food_list']
        for f in list(food_list.keys())[slider[1]:slider[2]]:
            a = bot.send_message(call.message.chat.id, f'{f} цена за шт. - {food_list[f]}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id, 0))
            sessions[call.message.chat.id]['last_foods'][a.message_id] = 0
        bot.send_message(call.message.chat.id, 'Навигация', reply_markup=slider[0])

    # Callback для кнопок + и -. UPD 02:1 18.11
    # Callback buttons + and -, I tend to think that it is shit code
    if call.data.split(';')[0] == 'fa':
        if call.data.split(';')[1] == '+':
            if call.message.text in sessions[call.message.chat.id]['cart']:
                sessions[call.message.chat.id]['cart'][call.message.text] += 1
            else:
                sessions[call.message.chat.id]['cart'][call.message.text] = 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['cart'][call.message.text]))
        if call.data.split(';')[1] == '-':
            if call.message.text in sessions[call.message.chat.id]['cart']:
                sessions[call.message.chat.id]['cart'][call.message.text] -= 1
                bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['cart'][call.message.text]))
                if sessions[call.message.chat.id]['cart'][call.message.text] == 0:
                    sessions[call.message.chat.id]['cart'].pop(call.message.text)
           

    # Переключение страниц блюд в категории с помощью слайдера
    # Switching dishes pages in categories with help of slider
    if call.data.split(';')[0] == 'fn':
        if call.data.split(';')[1] == 'forward':
            slider = gen_slider(int(call.data.split(';')[2])+1)                 
        elif call.data.split(';')[1] == 'back':
            slider = gen_slider(int(call.data.split(';')[2])-1)
        food_list = sessions[call.message.chat.id]['food_list']
        last_foods = sessions[call.message.chat.id]['last_foods']
        
        for id in last_foods: 
            print(sessions[call.message.chat.id]['last_foods'], id)
            sys.stdout.flush()
            bot.delete_message(chat_id=call.message.chat.id, message_id=id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        sessions[call.message.chat.id]['last_foods'] = {}

        for f in list(food_list.keys())[slider[1]:slider[2]]:
            a = bot.send_message(call.message.chat.id, f'{f} цена за шт. - {food_list[f]}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id))
            sessions[call.message.chat.id]['last_foods'][a.message_id] = 0
        bot.send_message(call.message.chat.id, 'Навигация', reply_markup=gen_slider(slider[3])[0])

    # Добавление позиций в корзину    
    # Adding dishes in cart
    if call.data.split(';')[0] == 'f':
        if call.data.split(';')[1] != '0':
            sessions[call.message.chat.id]['real_cart'][call.message.text.split(' цена за шт. - ')[0]] = int(call.data.split(';')[1])
        print(sessions[call.message.chat.id]['real_cart'])
        sys.stdout.flush() 
    
    if call.data.split(';')[0] == 'cart':
       
        for id in sessions[call.message.chat.id]['last_foods']:
            bot.delete_message(chat_id=call.message.chat.id, message_id=id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        sessions[call.message.chat.id]['last_foods'] = {}
        # just testing for future updates  
        if call.data == 'cart amongus':
            with open(r'photos\amogus.jpg', 'rb') as f:
                a = bot.send_photo(call.message.chat.id, f, 'amogus')
                print(a.photo[0].file_id)
                sys.stdout.flush()
            bot.edit_message_caption('amogud edited', call.message.chat.id, a.message_id)
        else:
            slider = gen_slider(1, name='cart', cal=call.message.chat.id)
            a = bot.send_message(call.message.chat.id, 'Корзина', reply_markup=None)
            sessions[call.message.chat.id]['cart_ids'].append(a.message_id)
            cart_items = sessions[call.message.chat.id]['real_cart']
            for item in list(cart_items.keys())[slider[1]:slider[2]]:
                a = bot.send_message(call.message.chat.id, item, reply_markup=gen_foods(item, call.message.chat.id, name='cart', temp=cart_items[item]))
                sessions[call.message.chat.id]['cart_ids'].append(a.message_id)
            a = bot.send_message(call.message.chat.id, 'Навигация', reply_markup=slider[0])
            sessions[call.message.chat.id]['cart_navigation'] = a.message_id
           
    # Навигация по корзине
    # Cart navigation
    if call.data.split(';')[0] == 'crt':
        cart_items = sessions[call.message.chat.id]['real_cart']
        if call.data.split(';')[1] == 'forward':
            slider = gen_slider(int(call.data.split(';')[2])+1, name='cart', cal=call.message.chat.id)
        elif call.data.split(';')[1] == 'back':
            slider = gen_slider(int(call.data.split(';')[2])-1, name='cart', cal=call.message.chat.id)
        
        for id in sessions[call.message.chat.id]['cart_ids'][1:]:
            bot.delete_message(chat_id=call.message.chat.id, message_id=id)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        sessions[call.message.chat.id]['cart_ids'] = [sessions[call.message.chat.id]['cart_ids'][0]]

        for item in list(cart_items.keys())[slider[1]:slider[2]]:
            a = bot.send_message(call.message.chat.id, item, reply_markup=gen_foods(item, call.message.chat.id, name='cart', temp=cart_items[item]))
            sessions[call.message.chat.id]['cart_ids'].append(a.message_id)
        a = bot.send_message(call.message.chat.id, 'Навигация', reply_markup=slider[0])
        sessions[call.message.chat.id]['cart_navigation'] = a.message_id
    # Изменение кол-ва позиций в корзине
    # Edding amount of dishes in cart
    if call.data.split(';')[0] == 'crta':
        if call.data.split(';')[1] == '+':
            sessions[call.message.chat.id]['real_cart'][call.message.text] += 1
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['real_cart'][call.message.text], name='cart'))
        elif call.data.split(';')[1] == '-':
            if sessions[call.message.chat.id]['real_cart'][call.message.text] > 1:
                sessions[call.message.chat.id]['real_cart'][call.message.text] -= 1
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=call.message.text, reply_markup=gen_foods(call.message.text, call.message.chat.id, sessions[call.message.chat.id]['real_cart'][call.message.text], name='cart'))
                if sessions[call.message.chat.id]['real_cart'][call.message.text] == 0:
                    sessions[call.message.chat.id]['real_cart'].pop(call.message.text)
            else:
                sessions[call.message.chat.id]['real_cart'].pop(call.message.text)
                sessions[call.message.chat.id]['cart_ids'].remove(call.message.message_id)
                slider = gen_slider(1, name='cart', cal=call.message.chat.id)
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=sessions[call.message.chat.id]['cart_navigation'], 
                                      text="Навигация", reply_markup=slider[0])
                bot.delete_message(call.message.chat.id, call.message.message_id)

    if call.data.split(';')[0] == 'o':
        order_message = ''
        price = 0
        print(db.get_item('Food', 'Кока-кола 0.5л в стекле', 'name'))

        for item in sessions[call.message.chat.id]['real_cart']:
                order_message += item + ', ' + str(sessions[call.message.chat.id]['real_cart'][item])+ ' шт. : ' + str(sessions[call.message.chat.id]['real_cart'][item] * db.get_item('Food', item, 'name')[0][2])+' руб' + '\n'
                price += sessions[call.message.chat.id]['real_cart'][item] * db.get_item('Food', item, 'name')[0][2]
        if call.data.split(';')[1] == 'o':
            for id in sessions[call.message.chat.id]['cart_ids']:
                bot.delete_message(chat_id=call.message.chat.id, message_id=id)
            for id in sessions[call.message.chat.id]['last_foods']:
                bot.delete_message(chat_id=call.message.chat.id, message_id=id)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            sessions[call.message.chat.id]['last_foods'] = {} 
            sessions[call.message.chat.id]['cart_ids'] = []
            order_message += f'Цена заказа: {price}' 
            bot.send_message(call.message.chat.id, order_message, reply_markup=key_order)

        if call.data.split(';')[1] == 'next':
            bot.delete_message(call.message.chat.id, call.message.message_id)
            a = bot.send_message(call.message.chat.id, f'{call.message.text}\nВведите адрес доставки: ', reply_markup=keyb_order_card)
            sessions[call.message.chat.id]['adress_info']['adress'] = f'{call.message.text}\nВведите адрес доставки:'
            sessions[call.message.chat.id]['adress_info']['id'] = a.message_id

        if call.data.split(';')[1] == 'finish':
            bot.send_message(call.message.chat.id, 'Ваш заказ:\n'+ sessions[call.message.chat.id]['adress_info']['adress'], reply_markup=keyb_finish)

    if call.data.split(';')[0] == 'adm':
        a = 0
        if call.data.split(';')[1] != 'apr':
            bot.delete_message(call.message.chat.id, call.message.message_id)
        if call.data.split(';')[1] == 'adm':
            a = bot.send_message(call.message.chat.id, 'Управление админами', reply_markup=keyb_admin_management)
        if call.data.split(';')[1] == 'ad':
            a = bot.send_message(call.message.chat.id, 'Введите никнейм пользователя, которого хотите сделать админом и его уровень.\nПример: "Никнейм" 1\n Админ и его уровень:', reply_markup=admin_management(call.data.split(';')[1]))
        if call.data.split(';')[1] == 'del':
            a = bot.send_message(call.message.chat.id, 'Введите никнейм админа, которого хотите удалить.\n Пример: "Никнейм"\n Админ:', reply_markup=admin_management(call.data.split(';')[1]))
        if call.data.split(';')[1] == 'ed':
            a = bot.send_message(call.message.chat.id, 'Введите никнейм админа, которого хотите изменить и уровень, который хотите ему присвоить.\nПример: "Никнейм" 1\n Админ и его уровень:', reply_markup=admin_management(call.data.split(';')[1]))
        
        if call.data.split(';')[1] == 'db':
            a = bot.send_message(call.message.chat.id, 'Что хотите изменить?', reply_markup=keyb_db_change)
        if call.data.split(';')[1] == 'back':
            a = bot.send_message(chat_id=call.message.chat.id, text = 'Панель управления', reply_markup=keyb_panel)
        # Подтверждение заказа TG
        if call.data.split(';')[1] == 'done':
            i_kb = InlineKeyboardMarkup()
            i_kb.add(InlineKeyboardButton('Отзыв', callback_data='o;review'))
            i_kb.add(InlineKeyboardButton('В меню', callback_data='m;0'))
            bot.edit_message_text(chat_id=int(call.data.split(';')[2][2:]),
                                  message_id=pending_orders[call.data.split(';')[2]]['message_id'],
                                  text='Спасибо что выбрали нас! Будем благодарны если вы оставите отзыв',
                                  reply_markup=i_kb)
            pending_orders.pop(call.data.split(';')[2])
        if call.data.split(';')[1] == 'apr':
            client_id = db.insert_client('name',  # later change to user first_name?
                                         pending_orders[call.data.split(';')[2]]['tel'],
                                         19,  # del age later
                                         pending_orders[call.data.split(';')[2]]['adress'],
                                         call.data.split(';')[2][:2],
                                         call.data.split(';')[2][2:])
            time_placed = str(time.localtime().tm_hour) + ':' + str(time.localtime().tm_min)
            delivery_time = db.insert_order(client_id,
                                            time_placed,
                                            db.get_item('Admins', call.from_user.id, 'tg_id')[0][0],
                                            pending_orders[call.data.split(';')[2]]['cart'])
            i_kb=InlineKeyboardMarkup()
            i_kb.add(InlineKeyboardButton('С моим заказом что-то не так',callback_data='o;wrong') )
            bot.edit_message_text(chat_id=int(call.data.split(';')[2][2:]),
                                  message_id=pending_orders[call.data.split(';')[2]]['message_id'],
                                  text='Ваш заказ будет доставлен через ' + str(delivery_time) + ' минут',
                                  reply_markup=i_kb)
            i_kb = InlineKeyboardMarkup()
            i_kb.add(InlineKeyboardButton('Заказ выполнен', callback_data='adm;done;'+call.data.split(';')[2]))
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text=call.message.text,
                                  reply_markup=i_kb)

        # Отклонение заказа TG
        if call.data.split(';')[1] == 'deca':
            i_kb = InlineKeyboardMarkup()
            i_kb.add(InlineKeyboardButton('Вернуться в меню', callback_data='m;0'))
            bot.edit_message_text(chat_id=int(call.data.split(';')[2][2:]),
                                  message_id=pending_orders[call.data.split(';')[2]]['message_id'],
                                  text='''Простите, но ваш адресс не входит в зону охвата доставки нашего 
ресторана, но вы можете посетить наш ресторан самостоятельно по адресу ул. Юайтишевская 42''',
                                  reply_markup=i_kb
                                  )
        if call.data.split(';')[1] == 'deco':
            i_kb = InlineKeyboardMarkup()
            i_kb.add(InlineKeyboardButton('Вернуться в корзину', callback_data='cart;0'))
            bot.edit_message_text(chat_id=int(call.data.split(';')[2][2:]),
                                  message_id=pending_orders[call.data.split(';')[2]]['message_id'],
                                  text='Вы некорректно заполнили ваши данные, пожалуйста, заполните данные для оформления заказа ещё раз',
                                  reply_markup=i_kb
                                  )
        if a and call.data.split(';')[1] != 'apr':
            admin_session[call.message.chat.id]['action_id'] = [a.message_id, call.data.split(';')[1]]
            admin_session[call.message.chat.id]['last_message'] = a.text

    if call.data.split(';')[1] == 'yes':
        if admin_session[call.message.chat.id]['last_message'] != call.message.text:
            if len(admin_session[call.message.chat.id]['admin_to_change'].split(' ')) == 2:
                id = db.get_item('Admins', admin_session[call.message.chat.id]['admin_to_change'].split()[0], 'name')
                if call.data.split(';')[0] == 'add':
                    # db.insert_admin()
                    pass
                elif call.data.split(';')[0] == 'del':
                    db.del_item('Admins', id[0][0])
                elif call.data.split(';')[0] == 'edit':
                    db.update_cell('Admins', id[0][0], 'role', admin_session[call.message.chat.id]['admin_to_change'].split()[1])
                    print(db.get_item('Admins', admin_session[call.message.chat.id]['admin_to_change'].split()[0], 'name'))
         
            admin_session[call.message.chat.id]['last_message'] = call.message.text
            bot.delete_message(call.message.chat.id, call.message.message_id)
            bot.send_message(call.message.chat.id, 'Управление админами', reply_markup=keyb_admin_management)

    if call.data == 'o;send':
        text = 'Ваш заказ ожидает подтверждения \n\n'
        total_sum = 0
        food_list = ''
        for food, amount in sessions[call.message.chat.id]['real_cart'].items():
            price = db.get_item('Food', food, 'name')[0][2]
            food_list += f"{food} * {amount} шт. = {price}\n"
            total_sum += price * amount
        text += sessions[call.message.chat.id]['adress_info']['adress']
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=text)
        adress = sessions[call.message.chat.id]['adress_info']['adress'].split('\n')[-1].split(': ')[1]
        send_order('TG', call.message.chat.id, adress, 375291234567, # change to tel later
                   call.message.message_id, sessions[call.message.chat.id]['real_cart'])

    if call.data.split(';')[0] == 'db':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        if call.data.split(';')[1] == 'change':
            bot.send_message(call.message.chat.id, "Меню", reply_markup=gen_menu(1, callback=('db', 'dbn'))[0])
        else:
            print(db.get_category(call.data.split(';')[1]))
            admin_session[call.message.chat.id]['food_list'] = db.get_category(call.data.split(';')[1])
            slider = gen_slider(1)
            for item in list(admin_session[call.message.chat.id]['food_list'])[slider[1]:slider[2]]:
                a = bot.send_message(call.message.chat.id, item, reply_markup=None)
                admin_session[call.message.chat.id]['last_foods'].append(a.message_id)
            bot.send_message(call.message.chat.id, 'Навигация', reply_markup=gen_slider(slider[3], name='db_change')[0])

    if call.data.split(';')[0] == 'dbf':
        if call.data.split(';')[1] == 'forward':
            slider = gen_slider(int(call.data.split(';')[2])+1, name='db_change')      
        if call.data.split(';')[1] == 'back': 
            slider = gen_slider(int(call.data.split(';')[2])-1, name='db_change') 

        food_list = admin_session[call.message.chat.id]['food_list']
        last_foods = admin_session[call.message.chat.id]['last_foods']
        
        if slider[1] < len(food_list) and slider[2] > 0:
            for id in last_foods: 
                bot.delete_message(chat_id=call.message.chat.id, message_id=id)
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            admin_session[call.message.chat.id]['last_foods'] = []
            
            for f in list(food_list.keys())[slider[1]:slider[2]]:
                a = bot.send_message(call.message.chat.id, f'{f}', reply_markup=gen_foods((f, food_list[f]), call.message.chat.id, name='db_change'))
                admin_session[call.message.chat.id]['last_foods'].append(a.message_id)
            bot.send_message(call.message.chat.id, 'Навигация', reply_markup=gen_slider(slider[3], name='db_change')[0])
    
    if call.data.split(';')[0] == 'dbn': 
        gen_menu_info = gen_menu(int(call.data.split(';')[2]), callback=('db', 'dbn'))
        if call.data.split(';')[1] == 'forward':
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Меню", reply_markup=gen_menu(gen_menu_info[1]+1, callback=('db', 'dbn'))[0])
        if call.data.split(';')[1] == 'back':
            if gen_menu_info[1] > 1:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Меню", reply_markup=gen_menu(gen_menu_info[1]-1, callback=('db', 'dbn'))[0])

    if call.data.split(';')[0] == 'panel':
        if admin_session[call.message.chat.id]['last_foods']:
            for id in admin_session[call.message.chat.id]['last_foods']:
                bot.delete_message(chat_id=call.message.chat.id, message_id=id)
            admin_session[call.message.chat.id]['last_foods'] = []
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
        bot.send_message(chat_id=call.message.chat.id, text = 'Панель управления', reply_markup=keyb_panel) 
        
    
print("Ready")

bot.infinity_polling()    

