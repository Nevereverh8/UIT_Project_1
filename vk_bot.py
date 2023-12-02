# -*- coding: utf-8-sig -*-
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import array
from db_requests import db
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telegram_bot import send_order

bot = telebot.TeleBot('6566836113:AAEROPk40h1gT7INUnWNPg2LEbYug6uDbns')
admin_chat_id = -1002019810166
GROUP_ID = '168407288'
GROUP_TOKEN = 'vk1.a.V_3LVLsyaa3Z-x1TlEmcrWA8fHL-aHH-MM5tYAAVF9qF7wwZTreoJvg187d8PG1bXEacBFTVi9jwfU8DyS-6DMmW6uPouJzV5NJl3nUL0KY855az30d9bbF5ZcnRXvC_1gPa_ZroL5sCosDoSlNj0lRAHkZNfinTvHVVUUv7YfmCEPtE_k0A0ysrGDJ1GivmCNmUxHGODcNy-tPhcvSdNA'
API_VERSION = '5.120'

# not so main globals
text_vk = """
Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана.\nВсе вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню\nЕсли клавиатура свернута, нажмите на 4 точки в правом нижнем углу!
"""
HI = ['s', 'start', 'Start', 'начать', 'Начало', 'Начать', 'начало', 'Бот', 'бот', 'Старт', 'старт', 'скидки', 'Скидки',
      'стартуй', 'бля', 'человек', 'бот', 'Бот', 'БОТ']

# main globals
sessions = {}

# Запускаем бот
vk_session = VkApi(token=GROUP_TOKEN, api_version=API_VERSION)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, group_id=GROUP_ID)

# Настройки клавиатур
settings = dict(one_time=False, inline=False)
settings2 = dict(one_time=False, inline=True)

# Основное меню
keyboard_1 = VkKeyboard(**settings)
keyboard_1.add_button(label="Меню!", color=VkKeyboardColor.NEGATIVE, payload={"type": "text"})
keyboard_1.add_line()
keyboard_1.add_callback_button(label='Зона доставки', color=VkKeyboardColor.POSITIVE,
                               payload={"type": "open_link",
                                        "link": "https://docs.google.com/spreadsheets/d/1FhYGE5IODqbtXSfQGBs0BGUaUJYAWBGAC2SRWqYzf6M"})
keyboard_1.add_line()
keyboard_1.add_callback_button(label='Мы в Телеграме!', color=VkKeyboardColor.PRIMARY,
                               payload={"type": "open_link", "link": "https://t.me/skidkinezagorami"})


# gen keyb 4 categories
def key_gen(list_, num, fix_poz=5, flag="x", flag2="f"):
    if len(list_) % 5 == 1:
        fix_poz = 4
    vkinl = VkKeyboard(**settings2)
    if ((num + 1) * fix_poz) < len(list_):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(list_)
    for x in range(num * fix_poz, end_):
        vkinl.add_callback_button(label=list_[x], color=VkKeyboardColor.SECONDARY,
                                  payload={"type": flag2 + ' ;' + list_[x] + '; ' + str(x)})
        vkinl.add_line()
    if num == 0 and end_ != len(list_):
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num + 1)})
    elif num != 0 and end_ == len(list_):
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num - 1)})
    elif num != 0:
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num + 1)})
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num - 1)})
    return vkinl


# a lil bit sure what 2 do
# записи сделать - Notion?
def key_gen_cat(dicty, num, fix_poz=3, flag="x", dicty_name=None, user_id=None):
    vkinl = VkKeyboard(**settings2)
    if ((num + 1) * fix_poz) < len(dicty):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(dicty)
    listy = [key for x in range(len(dicty)) for i, key in enumerate(dicty) if x == i]
    # print(listy)
    for x in range(num * fix_poz, end_):
        # change here
        death_id = send_message_event(listy[x], key_gen_pos(listy[x], user_id))
        # print(death_id)
        # death is only the beginning
        sessions[user_id]['death_squad'].append(death_id)
    if num == 0 and end_ != len(dicty):
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + dicty_name + '; ' + str(num + 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Ваш заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    elif num != 0 and end_ == len(dicty):
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + dicty_name + '; ' + str(num - 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Ваш заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    elif num != 0:
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + dicty_name + '; ' + str(num + 1)})
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + dicty_name + '; ' + str(num - 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Ваш заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    else:
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Ваш заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    # print(vkinl.keyboard)
    return vkinl


# double call if u want to change amount(кол-во)
def key_gen_pos(pos_name, user_id, change=0):
    cart_text = "Добавить в корзину"
    # стартовая проверка на существование в словарике
    if pos_name not in sessions[user_id]['temp']:
        sessions[user_id]['temp'][pos_name] = 0
        but_text = "Кол-во: 0"
    else:
        but_text = f"Кол-во: {sessions[user_id]['temp'][pos_name]}"
    # работа с temp при нажатии на "+" и "-"
    if change:
        result = sessions[user_id]['temp'][pos_name] + change
        if result >= 0:
            sessions[user_id]['temp'][pos_name] = result
    # изменение текста кнопки при изменении количества позиций после того как данные есть в корзине
    if pos_name in sessions[user_id]['cart']:
        if sessions[user_id]['temp'][pos_name] == sessions[user_id]['cart'][pos_name] and sessions[user_id]['cart'][
            pos_name] != 0:
            cart_text = 'Уже в корзине'
        elif sessions[user_id]['temp'][pos_name] != sessions[user_id]['cart'][pos_name] and sessions[user_id]['cart'][
            pos_name] != 0:
            cart_text = 'Изменить кол-во'
        else:
            cart_text = "Добавить в корзину"
    vkinl = VkKeyboard(**settings2)
    vkinl.add_callback_button(label="-", color=VkKeyboardColor.PRIMARY,
                              payload={"type": 'item' + ' ;' + pos_name + '; ' + str(-1)})
    vkinl.add_callback_button(label=but_text, color=VkKeyboardColor.PRIMARY,
                              payload={"type": ''})
    vkinl.add_callback_button(label="+", color=VkKeyboardColor.PRIMARY,
                              payload={"type": 'item' + ' ;' + pos_name + '; ' + str(1)})
    vkinl.add_line()
    vkinl.add_callback_button(label=cart_text, color=VkKeyboardColor.PRIMARY,
                              payload={"type": 'cart' + ' ;' + pos_name + '; ' + str(0)})
    return vkinl


def key_gen_cart(dicty, num, fix_poz=6, flag="x", user_id=None):
    vkinl = VkKeyboard(**settings2)
    if ((num + 1) * fix_poz) < len(dicty):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(dicty)
    listy = [key for x in range(len(dicty)) for i, key in enumerate(dicty) if x == i]
    # print(listy)
    for x in range(num * fix_poz, end_):
        death_id = send_message_event(listy[x], key_gen_pos_cart(listy[x], user_id))
        # death is only the beginning
        sessions[user_id]['death_squad'].append(death_id)
    if num == 0 and end_ != len(dicty):
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + '' + '; ' + str(num + 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    elif num != 0 and end_ == len(dicty):
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + '' + '; ' + str(num - 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    elif num != 0:
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + '' + '; ' + str(num + 1)})
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ;' + '' + '; ' + str(num - 1)})
        vkinl.add_line()
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    else:
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_callback_button(label="Оформить заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'inter' + ' ;' + '' + '; ' + str(0)})
    # print(vkinl.keyboard)
    return vkinl


# double call if u want to change amount(кол-во)
def key_gen_pos_cart(pos_name, user_id, change=0):
    # работа с temp при нажатии на "+" и "-"
    if change:
        result = sessions[user_id]['cart'][pos_name] + change
        if result >= 0:
            sessions[user_id]['cart'][pos_name] = result
    but_text = f"Кол-во: {sessions[user_id]['cart'][pos_name]}"
    vkinl = VkKeyboard(**settings2)
    vkinl.add_callback_button(label="-", color=VkKeyboardColor.PRIMARY,
                              payload={"type": 'c_item' + ' ;' + pos_name + '; ' + str(-1)})
    vkinl.add_callback_button(label=but_text, color=VkKeyboardColor.PRIMARY,
                              payload={"type": ''})
    vkinl.add_callback_button(label="+", color=VkKeyboardColor.PRIMARY,
                              payload={"type": 'c_item' + ' ;' + pos_name + '; ' + str(1)})
    return vkinl


def pos_temp_handler(pos_name, user_id):
    sessions[user_id]['cart'][pos_name] = sessions[user_id]['temp'][pos_name]
    keyb = key_gen_pos(pos_name, user_id)
    return keyb


def message_delete(listy, new=True):
    print(listy, "listy")
    if new:
        vk.messages.delete(peer_id=event.obj.message['from_id'],
                           message_ids=listy,
                           delete_for_all=True)
    else:
        vk.messages.delete(peer_id=event.obj.peer_id,
                           message_ids=listy,
                           delete_for_all=True)


def order_interbellum(iser_id):
    vkinl = VkKeyboard(**settings2)
    order_message = '\n*\n*\n*\n'
    total_price = 0
    if not all(value == 0 for key, value in sessions[iser_id]['cart'].items()):
        for key, value in sessions[iser_id]['cart'].items():
            if value > 0:
                price = db.get_item('Food', key, 'name')[0][2]
                order_message += f"""{key} X {value} шт. : {price} * {value} = {price * value} руб\n"""
                total_price += price * value
        order_message += f"""Цена заказа {total_price} руб\n"""
        vkinl.add_callback_button(label="Изменить заказ", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'change' + ' ;''; ' + str(0)})
        vkinl.add_callback_button(label="Продолжить", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": 'continue'})
    else:
        order_message += 'На данный момент вы ни чего не выбрали'
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    # message_delete(sessions[user_id]['death_leader'], new=False)
    return order_message, vkinl


# different send and editing mess func
def edit_message_new(message, mes_id, keyboard=None, peer=None):
    # print(message, mes_id)
    if peer:
        id_of_peer = peer
    else:
        id_of_peer = event.obj.message['from_id']
    if keyboard:
        vk.messages.edit(
            peer_id=id_of_peer,
            message_id=mes_id,
            message=message,
            keyboard=keyboard.get_keyboard())
    else:
        vk.messages.edit(
            peer_id=id_of_peer,
            message_id=mes_id,
            message=message)


# this func only for event get fucked new message cuz vkapi
def edit_message(message, keyboard=None, mes_id=None):
    # print(keyboard.keyboard)
    # for i in keyboard.keyboard['buttons']:
    #     print(i)
    if mes_id:
        id_ = mes_id
    else:
        id_ = event.obj.conversation_message_id
    if keyboard:
        internal_id = vk.messages.edit(
            peer_id=event.obj.peer_id,
            message=message,
            conversation_message_id=id_,
            keyboard=keyboard.get_keyboard())
    else:
        internal_id = vk.messages.edit(
            peer_id=event.obj.peer_id,
            message=message,
            conversation_message_id=id_)
    return internal_id


def send_message_event(message, keyboard=None):
    if keyboard:
        mes_id = vk.messages.send(
            user_id=event.object.user_id,
            random_id=0,
            peer_id=event.object.user_id,
            keyboard=keyboard.get_keyboard(),
            message=message)
    else:
        mes_id = vk.messages.send(
            user_id=event.object.user_id,
            random_id=0,
            peer_id=event.object.user_id,
            message=message)
    return mes_id


def send_message_new(message, keyboard=None):
    if keyboard:
        mes_id = vk.messages.send(
            user_id=event.obj.message['from_id'],
            random_id=0,
            peer_id=event.obj.message['from_id'],
            keyboard=keyboard.get_keyboard(),
            message=message)
    else:
        mes_id = vk.messages.send(
            user_id=event.obj.message['from_id'],
            random_id=0,
            peer_id=event.obj.message['from_id'],
            message=message)
    return mes_id


def adder_of_dict_sections_for_user(dicty, user_id):
    dicty[user_id]['temp'] = {}
    dicty[user_id]['cart'] = {}
    dicty[user_id]['death_squad'] = []
    dicty[user_id]['death_leader'] = []
    dicty[user_id]['edit_leader'] = 0
    dicty[user_id]['contacts'] = {}
    dicty[user_id]['credentials'] = {'flag_tel': False, 'flag_adr': False}


print("Ready")
for event in longpoll.listen():
    # новые сообщения
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['text'] != '':
            if event.from_user:
                user_id = event.obj.message['from_id']
                # создание словаря по id пользователя
                if user_id not in sessions:
                    sessions[user_id] = {}
                    adder_of_dict_sections_for_user(sessions, user_id)
                if sessions[user_id]['credentials']['flag_tel']:
                    pass
                if sessions[user_id]['credentials']['flag_adr']:
                    pass
                if event.obj.message['text'] == 'Запустить бота!' or event.obj.message['text'] == "Меню!":
                    if sessions[user_id]['edit_leader']:
                        message_delete([sessions[user_id]['edit_leader']])
                    if sessions[user_id]['death_squad']:
                        print(sessions[user_id]['death_squad'], 'death_squad')
                        message_delete(sessions[user_id]['death_squad'])
                        sessions[user_id]['death_squad'] = []
                    keyb = key_gen(db.get_categories(), 0, flag='c', flag2='cat')
                    last_id = send_message_new('Выбирай категорию', keyb)
                    sessions[user_id]['edit_leader'] = last_id
                elif event.obj.message['text'] in HI:
                    send_message_new(text_vk, keyboard_1)
                # print(sessions)
    # коллбэк
    elif event.type == VkBotEventType.MESSAGE_EVENT:
        if event.object.payload.get('type') != '':
            user_id = event.object.user_id
            # создание словаря по id пользователя
            if event.object.user_id not in sessions:
                sessions[event.object.user_id] = {}
                adder_of_dict_sections_for_user(sessions, event.object.user_id)
            flag = event.object.payload.get('type').split()[0]
            data = event.object.payload.get('type').split()[-1]
            # print(flag, data)
            if event.object.payload.get('type') == 'open_link':
                vk.messages.sendMessageEventAnswer(
                    event_id=event.object.event_id,
                    user_id=event.object.user_id,
                    peer_id=event.object.peer_id,
                    event_data=json.dumps(event.object.payload))
            # old design and good enough
            elif flag == 'c':
                keyb = key_gen(db.get_categories(), int(data), flag='c', flag2='cat')
                last_id = edit_message('Выбирай категорию', keyb)
            elif flag == 'cat':
                dicty_of_item = db.get_category(event.object.payload.get('type').split(';')[1])
                keyb = key_gen_cat(dicty_of_item, 0, flag='i',
                                   dicty_name=event.object.payload.get('type').split(';')[1],
                                   user_id=event.object.user_id)
                if not dicty_of_item:
                    last_id = edit_message('В данной категории на данный момент нет товаров', keyb)
                else:
                    last_id = edit_message('Навигация', keyb)
            elif flag == 'i':
                if sessions[event.object.user_id]['death_squad']:
                    message_delete(sessions[event.object.user_id]['death_squad'], new=False)
                    sessions[event.object.user_id]['death_squad'] = []
                dicty_of_item = db.get_category(event.object.payload.get('type').split(';')[1])
                keyb = key_gen_cat(dicty_of_item, int(data), flag='i',
                                   dicty_name=event.object.payload.get('type').split(';')[1],
                                   user_id=event.object.user_id)
                last_id = edit_message('Навигация', keyb)

            elif flag == 'item':
                name = event.object.payload.get('type').split(';')[1]
                # print(name, user_id, int(data))
                keyb = key_gen_pos(name, user_id, int(data))
                keyb = key_gen_pos(name, user_id)
                last_id = edit_message(name, keyb)
            elif flag == 'cart':
                name = event.object.payload.get('type').split(';')[1]
                keyb = pos_temp_handler(name, user_id)
                keyb = key_gen_pos(name, user_id)
                last_id = edit_message(name, keyb)
                # send_order('VK', user_id, 'Кольцова 42', '+375291825903', 'message_id', sessions[user_id]['cart'])
            elif flag == 'inter':
                print(sessions[user_id]['edit_leader'], 'edit_leader')
                if sessions[user_id]['death_squad']:
                    message_delete(sessions[user_id]['death_squad'], new=False)
                    sessions[user_id]['death_squad'] = []
                if sessions[user_id]['edit_leader']:
                    # FFS FFS FFS LEON Halp
                    edit_message_new('*', sessions[user_id]['edit_leader'], peer=user_id)
                    # edit_message('*', mes_id=sessions[user_id]['edit_leader'])
                    sessions[user_id]['edit_leader'] = 0
                mess, keyb = order_interbellum(user_id)
                last_id = send_message_event(mess, keyb)
                sessions[user_id]['death_leader'] = last_id
            elif flag == 'continue':
                # work work
                print(sessions[user_id]['death_leader'])
                send_order('VK', user_id, 'Кольцова 42', '+375291825903', sessions[user_id]['death_leader'],
                           sessions[user_id]['cart'])
            elif flag == 'change':
                if sessions[user_id]['death_leader']:
                    message_delete([sessions[user_id]['death_leader']], new=False)
                keyb = key_gen_cart(sessions[user_id]['cart'], 0, flag='m_item', user_id=user_id)
                last_id = send_message_event('Навигация', keyb)
                sessions[user_id]['edit_leader'] = last_id
            elif flag == 'm_item':
                message_delete(sessions[event.object.user_id]['death_squad'], new=False)
                sessions[event.object.user_id]['death_squad'] = []
                keyb = key_gen_cart(sessions[user_id]['cart'], int(data), flag='m_item', user_id=user_id)
                last_id = edit_message('Навигация', keyb)
            elif flag == 'c_item':
                name = event.object.payload.get('type').split(';')[1]
                keyb = key_gen_pos_cart(name, user_id, int(data))
                last_id = edit_message(name, keyb)
            # print(event)
            # print(sessions[user_id]['temp'])
            # print(sessions[user_id]['cart'])
            print(sessions[user_id]['edit_leader'], 'edit_leader2')

            # Отправка заказа в телегу
            if event.object.payload.get('type') == 'send_order':  # <-суда колбек когда все кончено
                send_order('VK', user_id, 'Кольцова 42', '+375291825903', 'message_id', sessions[user_id]['cart'])
"""
теперь это легаси но пусть лежит наверное
upload = vk_api.VkUpload(vk)
photo = upload.photo_messages('вашфайл')
owner_id = photo[0]['owner_id']
photo_id = photo[0]['id']
access_key = photo[0]['access_key']
attachment = f'photo{owner_id}_{photo_id}_{access_key}'
attachment = attachment
vk.method("messages.send", {"peer_id": id, "message": "TEST", "attachment": "photo-57846937_457307562", "random_id": 0})
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=0,
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_1.get_keyboard(),
                        message=text_vk,
                        attachment="photos/amogus.jpg")
"""
# message_delete(sessions[user_id]['death_squad'], new=False)
# message_delete(sessions[user_id]['death_leader'], new=False)
