# -*- coding: utf-8-sig -*-
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import array
from db_requests import db



GROUP_ID = '168407288'
GROUP_TOKEN = 'vk1.a.V_3LVLsyaa3Z-x1TlEmcrWA8fHL-aHH-MM5tYAAVF9qF7wwZTreoJvg187d8PG1bXEacBFTVi9jwfU8DyS-6DMmW6uPouJzV5NJl3nUL0KY855az30d9bbF5ZcnRXvC_1gPa_ZroL5sCosDoSlNj0lRAHkZNfinTvHVVUUv7YfmCEPtE_k0A0ysrGDJ1GivmCNmUxHGODcNy-tPhcvSdNA'
API_VERSION = '5.120'

text_vk = """
Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана.\nВсе вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню\nЕсли клавиатура свернута, нажмите на 4 точки в правом нижнем углу!
"""
HI = "s start Start начать Начало Начать начало Бот бот Старт старт скидки Скидки puta madre стартуй бля ztart retard кожаный мешок человек бот Бот БОТ"
HI = ['s', 'start', 'Start', 'начать', 'Начало', 'Начать', 'начало', 'Бот', 'бот', 'Старт', 'старт', 'скидки', 'Скидки', 'puta', 'madre', 'стартуй', 'бля', 'ztart', 'retard', 'кожаный', 'мешок', 'человек', 'бот', 'Бот', 'БОТ']

#main globals
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
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    elif num != 0:
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num + 1)})
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num - 1)})
    else:
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    return vkinl

# not sure what 2 do
def key_gen_cat(dicty, num, fix_poz=3, flag="x", flag2="f", dicty_name=None):
    vkinl = VkKeyboard(**settings2)
    if ((num + 1) * fix_poz) < len(dicty):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(dicty)
    listy = [key for x in range(len(dicty)) for i, key in enumerate(dicty) if x == i]
    # print(listy)
    for x in range(num * fix_poz, end_):
        # print(x)
        vkinl.add_callback_button(label=listy[x], color=VkKeyboardColor.SECONDARY,
                                  payload={"type": flag2 + ' ;' + listy[x] + '; ' + str(x)})
        vkinl.add_line()
    if num == 0 and end_ != len(dicty):
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num + 1)})
    elif num != 0 and end_ == len(dicty):
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num - 1)})
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    elif num != 0:
        vkinl.add_callback_button(label="Next", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num + 1)})
        vkinl.add_callback_button(label="Back", color=VkKeyboardColor.PRIMARY,
                                  payload={"type": flag + ' ' + str(num - 1)})
    else:
        vkinl.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
        vkinl.add_button(label="Корзина", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})
    return vkinl

def position_creation(food_name, change = 0):
    pass

# different send and editing mess func
# this func only for event get fucked new message cuz vkapi
def edit_message(message, keyboard=None):
    # print(keyboard.keyboard)
    # for i in keyboard.keyboard['buttons']:
    #     print(i)
    if keyboard:
        vk.messages.edit(
            peer_id=event.obj.peer_id,
            message=message,
            conversation_message_id=event.obj.conversation_message_id,
            keyboard=keyboard.get_keyboard())
    else:
        vk.messages.edit(
            peer_id=event.obj.peer_id,
            message=message,
            conversation_message_id=event.obj.conversation_message_id)

def send_message_event(message, keyboard=None):
    if keyboard:
        vk.messages.send(
            user_id=event.object.user_id,
            random_id=0,
            peer_id=event.object.user_id,
            keyboard=keyboard.get_keyboard(),
            message=message)
    else:
        vk.messages.send(
            user_id=event.object.user_id,
            random_id=0,
            peer_id=event.object.user_id,
            message=message)

def send_message_new(message, keyboard=None):
    if keyboard:
        vk.messages.send(
            user_id=event.obj.message['from_id'],
            random_id=0,
            peer_id=event.obj.message['from_id'],
            keyboard=keyboard.get_keyboard(),
            message=message)
    else:
        vk.messages.send(
            user_id=event.obj.message['from_id'],
            random_id=0,
            peer_id=event.obj.message['from_id'],
            message=message)

def adder_of_dict_sections_for_user(dicty, user_id):
    dicty[user_id]['temp'] = {}

print("Ready")
for event in longpoll.listen():
    # новые сообщения
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['text'] != '':
            if event.from_user:
                # создание словаря по id пользователя
                if event.obj.message['from_id'] not in sessions:
                    sessions[event.obj.message['from_id']] = {}
                    adder_of_dict_sections_for_user(sessions, event.obj.message['from_id'])
                print(event.obj.message)
                if event.obj.message['text'] == 'Запустить бота!' or event.obj.message['text'] == "Меню!":
                    print(event.obj.conversation_message_id, "event.obj.conversation_message_id")
                    keyb = key_gen(db.get_categories(), 0, flag='c', flag2='cat')
                    send_message_new('Выбирай категорию', keyb)
                elif event.obj.message['text'] in HI:
                    print(event.obj.conversation_message_id , "event.obj.conversation_message_id")
                    a = send_message_new(text_vk, keyboard_1)
                    # keyb = key_gen(db.get_categories(), 0, flag='c', flag2='cat')
                    # edit_message('Выбирай категорию', keyb)
                # print(sessions)
    # коллбэк
    elif event.type == VkBotEventType.MESSAGE_EVENT:
        # создание словаря по id пользователя
        if event.object.user_id not in sessions:
            sessions[event.object.user_id] = {}
            adder_of_dict_sections_for_user(sessions, event.object.user_id)
        # print(event.object.payload.get('type'))
        # print(event.object)
        # print(event.object.user_id, 'event.object.user_id')

        flag = event.object.payload.get('type').split()[0]
        data = event.object.payload.get('type').split()[-1]
        if event.object.payload.get('type') == 'open_link':
            print(event.obj.conversation_message_id , "event.obj.conversation_message_id")
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        # old design and good enough
        elif flag == 'c':
            # print(event.object)
            print(event.obj.conversation_message_id , "event.obj.conversation_message_id")
            keyb = key_gen(db.get_categories(), int(data), flag='c', flag2='cat')
            last_id = edit_message('Выбирай категорию', keyb)
            # print(last_id)
        # redo this shit |
        elif flag == 'cat':
            print(event.obj.conversation_message_id , "event.obj.conversation_message_id")
            # print(event.object.payload.get('type').split(';')[1])
            dicty_of_item = db.get_category(event.object.payload.get('type').split(';')[1])
            # print(dicty_of_item, "dicty_of_item")
            keyb = key_gen_cat(dicty_of_item, 0, flag='i', flag2='item',
                               dicty_name=event.object.payload.get('type').split(';')[1])
            last_id = edit_message('Выбирай магазин', keyb)
        elif flag == 'i':
            print(event.obj.conversation_message_id , "event.obj.conversation_message_id")
            # print(event.object.payload.get('type'))
            # print(int(data))
            # FIX
            keyb = key_gen_cat(dicty_of_item, int(data), flag='i', flag2='item')
            last_id = edit_message('Выбирай магазин', keyb)
        # print(sessions)
        # elif flag == 'item':
        #     last_id = message_edit(f"{' '.join(sec_dicty[event.object.payload.get('type').split(';')[1]])}",
        #                            keyboard_quit)



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