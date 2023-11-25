# -*- coding: utf-8-sig -*-
from vk_api import VkApi
from vk_api.utils import get_random_id
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import json
import array
from db_requests import db



GROUP_ID = '222668747'
GROUP_TOKEN = 'vk1.a.JpminctigYnNEjIZ_Ldi5ziq9ypj8z7lolFaFkrv0Mj9KuOtSJTihFBkls-JUOeodgvKfeKK0kc1xgJNPk10C720qXUt9KH5rNCJ4iRrSVOMdQYOvTy0ZGTLkKsCzx8CsEzpMAbeKmKW8vLpj4XefJth2TGf6goUHJuFryMA_Odg5DJcKS2dSkf3BVquMLsTZaMJ1u_OJxqjJyafUCk09w'
API_VERSION = '5.120'

text_vk = """
Приветсвуем в ресторане UIT.\nУютная, доброжелательная атмосфера и достойный сервис  - это основные преимущества ресторана.\nВсе вышеперечисленное и плюс доступный уровень цен позволили заведению оказаться в списке лучших ресторанов Минска xd. \n\n Можете ознакомится с меню, нажав кнопку меню\nЕсли клавиатура свернута, нажмите на 4 точки в правом нижнем углу!
"""
HI = "s start Start начать Начало Начать начало Бот бот Старт старт скидки Скидки puta madre стартуй бля ztart retard кожаный мешок человек бот Бот БОТ"

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

keyboard_quit = VkKeyboard(**settings2)
keyboard_quit.add_button(label="Меню!", color=VkKeyboardColor.PRIMARY, payload={"type": "text"})


def key_gen(list_, num, fix_poz=5, flag="x", flag2="f"):
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


def key_gen_cat(dicty, num, fix_poz=3, flag="x", flag2="f"):
    vkinl = VkKeyboard(**settings2)
    if ((num + 1) * fix_poz) < len(dicty):
        end_ = ((num + 1) * fix_poz)
    else:
        end_ = len(dicty)
    listy = [key for x in range(len(dicty)) for i, key in enumerate(dicty) if x == i]
    for x in range(num * fix_poz, end_):
        print(x)
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


# naming ok
def edit_message(message, keyboard):
    # print(keyboard.keyboard)
    # for i in keyboard.keyboard['buttons']:
    #     print(i)
    vk.messages.edit(
        peer_id=event.obj.peer_id,
        message=message,
        conversation_message_id=event.obj.conversation_message_id,
        keyboard=keyboard.get_keyboard())

# too
def send_message(message, keyboard):
    vk.messages.send(
        user_id=event.obj.message['from_id'],
        random_id=0,
        peer_id=event.obj.message['from_id'],
        keyboard=keyboard.get_keyboard(),
        message=message)
    return event.obj.message['from_id']
def adder_of_dict_sections_for_user(dicty, user_id):
    dicty[user_id]['temp'] = {}

print("Ready")
for event in longpoll.listen():
    # print(sessions)
    # новые сообщения
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['text'] != '':
            if event.from_user:
                # создание словаря по id пользователя
                if event.obj.message['from_id'] not in sessions:
                    sessions[event.obj.message['from_id']] = {}
                    adder_of_dict_sections_for_user(sessions, event.obj.message['from_id'])
                # print(event.obj.message['text'])
                if event.obj.message['text'] == 'Запустить бота!' or event.obj.message['text'] == "Меню!":
                    keyb = key_gen(db.get_categories(), 0, flag='c', flag2='cat')
                    send_message('Выбирай категорию', keyb)
                elif event.obj.message['text'] in HI:
                    send_message(text_vk, keyboard_1)
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
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        elif flag == 'c':
            # print(event.object)
            keyb = key_gen(db.get_categories(), int(data), flag='c', flag2='cat')
            last_id = edit_message('Выбирай категорию', keyb)
            # print(last_id)
        elif flag == 'cat':
            # print(event.object.payload.get('type').split(';')[1])
            dicty_of_item = db.get_category(event.object.payload.get('type').split(';')[1])
            # print(dicty_of_item, "dicty_of_item")
            keyb = key_gen_cat(dicty_of_item, 0, flag='i', flag2='item')
            last_id = edit_message('Выбирай магазин', keyb)
        elif flag == 'i':
            print(event.object.payload.get('type'))
            print(int(data))
            dicty_of_item = db.get_category(event.object.payload.get('type').split(';')[1])
            keyb = key_gen_cat(dicty_of_item, int(data), flag='i', flag2='item')
            last_id = edit_message('Выбирай магазин', keyb)
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