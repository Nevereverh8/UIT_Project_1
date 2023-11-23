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
HI = "start Start начать Начало Начать начало Бот бот Старт старт скидки Скидки puta madre стартуй бля ztart retard кожаный мешок человек бот Бот БОТ"

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

# naming ok
def edit_message(message, keyboard):
    return vk.messages.edit(
        peer_id=event.obj.peer_id,
        message=message,
        conversation_message_id=event.obj.conversation_message_id,
        keyboard=keyboard.get_keyboard())
# too
def send_message(message, keyboard):
    return vk.messages.edit(
        peer_id=event.obj.peer_id,
        message=message,
        conversation_message_id=event.obj.conversation_message_id,
        keyboard=keyboard.get_keyboard())


print("Ready")
for event in longpoll.listen():
    # новые сообщения
    if event.type == VkBotEventType.MESSAGE_NEW:
        if event.obj.message['text'] != '':
            if event.from_user:
                print(event.obj.message['text'])
                if event.obj.message['text'] == 'Запустить бота!' or event.obj.message['text'] == "Меню!":
                    keyb = key_gen(db.get_categories(), 0, flag='c', flag2='cat')
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=0,
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyb.get_keyboard(),
                        message='Выбирай категорию')
                elif event.obj.message['text'] in HI:
                    vk.messages.send(
                        user_id=event.obj.message['from_id'],
                        random_id=0,
                        peer_id=event.obj.message['from_id'],
                        keyboard=keyboard_1.get_keyboard(),
                        message=text_vk)
    # коллбэк
    elif event.type == VkBotEventType.MESSAGE_EVENT:
        print(event.object.payload.get('type'))
        flag = event.object.payload.get('type').split()[0]
        data = event.object.payload.get('type').split()[-1]
        if event.object.payload.get('type') == 'open_link':
            vk.messages.sendMessageEventAnswer(
                event_id=event.object.event_id,
                user_id=event.object.user_id,
                peer_id=event.object.peer_id,
                event_data=json.dumps(event.object.payload))
        elif flag == 'c':
            keyb = key_gen(db.get_categories(), int(data), flag='c', flag2='cat')
            last_id = edit_matrix('Выбирай категорию', keyb)
        elif flag == 'cat':
            list_of_item = first_dicty[event.object.payload.get('type').split(';')[1]]
            keyb = key_gen(list_of_item, 0, flag='i', flag2='item')
            last_id = edit_matrix('Выбирай магазин', keyb)
        # elif flag == 'i':
        #     keyb = key_gen(list_of_item, int(data), flag='i', flag2='item')
        #     last_id = message_edit('Выбирай магазин', keyb)
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
"""