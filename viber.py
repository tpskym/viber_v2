import os
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
import requests
import logging
from flask import Flask, request, Response
import psycopg2
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import json


def SaveStateToPostgress(sender_id, state_id, carousel_id, data_user, data):
    data_user_string = json.dumps(data_user)
    data_bot_string = json.dumps(data)
    state = True
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Open a cursor to perform database operations

        cur = conn.cursor()

        need_drop = True
        cur.execute("select * from information_schema.tables where table_name=%s", ('data_users',))
        if(cur.rowcount == 0):
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE data_users (id serial PRIMARY KEY, sender_id varchar(50), state_id varchar(36), carousel_id varchar(36),data_user text, data text );")
            need_drop = False

        if need_drop:
            cur.execute("DELETE FROM data_users WHERE sender_id = %s", (sender_id,));
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        cur.execute("INSERT INTO data_users (sender_id, state_id, carousel_id, data_user, data) VALUES (%s, %s, %s, %s, %s)",
              (sender_id, state_id, carousel_id, data_user_string, data_bot_string))

       # Make the changes to the database persistent
        conn.commit()
        # Close communication with the database
    except:
        state = False
    finally:
        cur.close()
        conn.close()
    return state

def RestoreStateFromPostgress(sender_id):
    state = False
    is_error = False
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Open a cursor to perform database operations
        cur = conn.cursor()

        cur.execute("select * from information_schema.tables where table_name=%s", ('data_users',))
        if(cur.rowcount == 0):
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE data_users (id serial PRIMARY KEY, sender_id varchar(50), state_id varchar(36), carousel_id varchar(36),data_user text, data text );")
            conn.commit()
            restore_ok = False

        if not restore_ok:
            return {'error': is_error, 'state' : False}
        cur.execute("SELECT sender_id,  state_id,  carousel_id, data_user,  data FROM data_users WHERE sender_id = %s", (sender_id,))
        result_query = cur.fetchone()
        if(not result_query == None):
            return {'state':True, 'sender_id':result_query[0], 'state_id':result_query[1], 'carousel_id':result_query[2],'data_user':json.loads(result_query[3]), 'data':json.loads(result_query[4])}
        else:
            return {'error': is_error, 'state' : False}

        # Make the changes to the database persistent

        # Close communication with the database
    except:
        is_error = True
        restore_ok = False
    finally:
        cur.close()
        conn.close()
    return {'error': is_error, 'state' : state}

address_api_itilium = os.environ['AddressApiItilium']
login_itilium = os.environ['LoginItilium']
password_itilium = os.environ['PasswordItilium']
auth_token_out = os.environ['AuthToken']

def GetTextCommand(message):
    text = ""
    if (isinstance(message, str)):
        text = message
    elif (isinstance(message, TextMessage)):
        text = message.text
    else:
        text = message.text
    return text

def GetIdErrorState():
    return "095761bb-67d8-455b-bf09-4e32d0e8dc4f" #Выбор действия

def ShowCarousel(sender_id, result_list, number_parts):

    max_buttons = 42
    if (len(result_list) > max_buttons ):
        count_in_part = max_buttons
        first_number = number_parts * count_in_part - count_in_part
        last_number = first_number + count_in_part - 1
        index = 0
        buttons = []
        isEnd = True
        for id_cortage, title_cortage, detail_text_cortage in result_list:
            id = id_cortage
            view = title_cortage
            detail_view = detail_text_cortage
            if (index > last_number):
                isEnd = False
                break
            elif index >= first_number:
                buttons.append({"TextVAlign": "top", "TextHAlign": "left", "ActionBody": id, "ActionType":"reply", "Text": view})
            index += 1
        buttons_keyboard = []
        if (isEnd == False):
            buttons_keyboard.append({"Columns": 6, "Rows": 1, "ActionBody": "more_data", "Text": "ЕЩЕ"})
        buttons_keyboard.append({"Columns": 6, "Rows": 1, "ActionBody": "cancel", "Text": "Отменить"})
        text_keyboard = {"Type": "keyboard","InputFieldState": "hidden", "Buttons": buttons_keyboard}
        viber.send_messages(sender_id, [RichMediaMessage(min_api_version=4, rich_media={"Type": "rich_media", "BgColor": "#FFFFFF",
                                                          "Buttons":buttons}), KeyboardMessage(
                                                                   keyboard=text_keyboard, min_api_version=4)])
    else:
        text_keyboard = {"Type": "keyboard", "InputFieldState": "hidden"}
        buttons = []
        buttons_keyboard = []
        for wrapper in result_list:
            id = id_cortage
            view = title_cortage
            detail_view = detail_text_cortage
            buttons.append({"TextVAlign": "top", "TextHAlign": "left", "ActionBody": id, "Text": view})
        buttons_keyboard.append({"Columns": 6, "Rows": 1, "ActionBody": "cancel", "Text": "Отменить"})
        text_keyboard.update({"Buttons": buttons_keyboard})
        viber.send_messages(sender_id, [RichMediaMessage(min_api_version=4, rich_media={"Type": "rich_media", "BgColor": "#FFFFFF",
                                                            "Buttons":buttons}), KeyboardMessage(
                                                                     keyboard=text_keyboard, min_api_version=4)])

def SaveState(sender_id, state_id, data, data_user, carousel_id):
    if SaveStateToPostgress(sender_id, state_id, carousel_id, data_user, data):
        return True
    else:
        return False

def RestoreState(sender_id):
    result_dict = RestoreStateFromPostgress(sender_id)
    if result_dict.get('state') == True:
         return (True, result_dict.get('state_id'), result_dict.get('data'), result_dict.get('data_user'), result_dict.get('carousel_id'))
    else:
         return (False,  ", ", ", ")




def proc02957edd8e984dd4a0aa530f15bba971(sender_id, message, data, service_data_bot_need, carousel_id):
    #Приветствие (программный выбор)
    viber.send_messages(sender_id, TextMessage(text="Добрый день!"))
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function02957edd8e984dd4a0aa530f15bba971(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "1":
        proc1b68be2d5a9a4d06adb59b874e1673ea(sender_id, message, data, service_data_bot_need, carousel_id) #Ввод секретного кода
    elif result_programm_select == "2":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия
    return

def proc_function02957edd8e984dd4a0aa530f15bba971(sender_id, message, data, service_data_bot_need, carousel_id):
    #Приветствие (функция программного выбора)
    if(id == "aq"):
        return "1"
    else:
        return "2"

def proc1b68be2d5a9a4d06adb59b874e1673ea(sender_id, message, data, service_data_bot_need, carousel_id):
    #Ввод секретного кода (выбор по результатам ввода с клавиатуры)
    viber.send_messages(sender_id, TextMessage(text="Введите секретный код"))
    if not SaveState(sender_id, "42e116a3-1716-47af-95a4-27feea6b8678", service_data_bot_need, data, carousel_id): #proc_function_expect_user1b68be2d5a9a4d06adb59b874e1673ea
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_function_expect_user1b68be2d5a9a4d06adb59b874e1673ea(sender_id, message, data, service_data_bot_need, carousel_id):
    if not isinstance(data, dict):
        data = {}
    text = GetTextCommand(message)
    result_programm_select = proc_function1b68be2d5a9a4d06adb59b874e1673ea(sender_id, text, data, carousel_id)
    if result_programm_select == "1":
        proc2b3f0bd4eef0409c9ffb14ffb0d21861(sender_id, message, data, service_data_bot_need, carousel_id) #Секретный код неверный
    elif result_programm_select == "2":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proc_function1b68be2d5a9a4d06adb59b874e1673ea(sender_id, text, data, carousel_id):
    #Ввод секретного кода (функция обработки выбора с клавиатуры)
    if text == "OK@":
        return "1"
    else:
        return "2"

def proc2b3f0bd4eef0409c9ffb14ffb0d21861(sender_id, message, data, service_data_bot_need, carousel_id):
    #Секретный код неверный
    viber.send_messages(sender_id, TextMessage(text="Секретный код неверный!"))
    proc1b68be2d5a9a4d06adb59b874e1673ea(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Ввод секретного кода
    return

def proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id):
    #Выбор действия (выбор из подчиненных команд)
    if not SaveState(sender_id, "1571b3a5-ce91-474f-b189-2987ba84c8d8", service_data_bot_need, data, carousel_id): #proc095761bb67d8455bbf094e32d0e8dc4f
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Выберите действие"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "f6829c8b-eb46-4c61-8ab6-3bd31f6bc879",
        "Text": "Мои обращения" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "11fe0cd9-823f-4515-909f-f0df1baccf1a",
        "Text": "Мои согласования" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "e7330888-8cc6-44ee-a230-a5c12d47ffd3",
        "Text": "Последние сообщения" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "5160f46d-71b8-466a-8b28-db1bf17d5392",
        "Text": "Обращения для подтверждения" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons": buttons}))
    if not SaveState(sender_id, "3350e75b-c2b2-4771-a4ae-2bde1f591295", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click095761bb67d8455bbf094e32d0e8dc4f
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id):
    #Выбор действия (Обработчик выбора из подчиненных команд)
    command = GetTextCommand(message)
    if command == "f6829c8b-eb46-4c61-8ab6-3bd31f6bc879":
        procf6829c8beb464c618ab63bd31f6bc879(sender_id, message, data, service_data_bot_need, carousel_id) #Мои обращения
    elif command == "11fe0cd9-823f-4515-909f-f0df1baccf1a":
        proc11fe0cd9823f4515909ff0df1baccf1a(sender_id, message, data, service_data_bot_need, carousel_id) #Мои согласования
    elif command == "e7330888-8cc6-44ee-a230-a5c12d47ffd3":
        proce73308888cc644eea230a5c12d47ffd3(sender_id, message, data, service_data_bot_need, carousel_id) #Последние сообщения
    elif command == "5160f46d-71b8-466a-8b28-db1bf17d5392":
        proc5160f46d71b8466a8b28db1bf17d5392(sender_id, message, data, service_data_bot_need, carousel_id) #Обращения для подтверждения
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def procf6829c8beb464c618ab63bd31f6bc879(sender_id, message, data, service_data_bot_need, carousel_id):
    #Мои обращения (Карусель)
    if not SaveState(sender_id, "6fd6a6df-765d-44e4-b2cf-04fee4be35d2", service_data_bot_need, data, carousel_id): #procf6829c8beb464c618ab63bd31f6bc879
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return

    number_parts = 1;
    temp = service_data_bot_need.get("number_partsf6829c8beb464c618ab63bd31f6bc879")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_cortegesf6829c8beb464c618ab63bd31f6bc879(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_partsf6829c8beb464c618ab63bd31f6bc879":number_parts})
        if not SaveState(sender_id, "272935d4-48b8-405b-96ab-fdf65d9c133d", service_data_bot_need, data, carousel_id): #proc_expect_comand_userf6829c8beb464c618ab63bd31f6bc879
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    elif result_list == "1":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия
    return

def proc_get_list_cortegesf6829c8beb464c618ab63bd31f6bc879(sender_id, data, carousel_id)
    #Мои обращения (получение списка кортежей)



def proc_expect_comand_userf6829c8beb464c618ab63bd31f6bc879(sender_id, message, data, service_data_bot_need, carousel_id)
    #Мои обращения (обработчик выбора пользователя из карусели или команды под ней)
    id = GetTextCommand(message)
    if id == "cancel":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_partsf6829c8beb464c618ab63bd31f6bc879")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_partsf6829c8beb464c618ab63bd31f6bc879": number_parts + 1})
        procf6829c8beb464c618ab63bd31f6bc879(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        procea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод элемента карусели (Вывод элемента карусели)
        proc17c11a9477c8493db93470bdbee77ffc(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусели (Вывод команд для выбранного элемента карусели)
    return

def procea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод элемента карусели

    detail_view = proc_get_user_detail_view_by_idea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, carousel_id, data)
    viber.send_messages(sender_id, TextMessage(text=detail_view))
    return

def proc_get_user_detail_view_by_idea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, element_id, data)
    #Вывод элемента карусели (функция получения детального представления выбранного элемента карусели)


def proc17c11a9477c8493db93470bdbee77ffc(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (команды элемента карусели)
    if not SaveState(sender_id, "238a9170-e105-4bcf-872d-ba0f6194eb0c", service_data_bot_need, data, carousel_id): #proc17c11a9477c8493db93470bdbee77ffc
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    buttons = []
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons})
    if not SaveState(sender_id, "41d299c9-5fee-4f00-b41f-1a6c53b8d555", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click17c11a9477c8493db93470bdbee77ffc
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click17c11a9477c8493db93470bdbee77ffc(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (Обработчик выбора из подчиненных команд элемента карусели)
    command = GetTextCommand(message)
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proc11fe0cd9823f4515909ff0df1baccf1a(sender_id, message, data, service_data_bot_need, carousel_id):
    #Мои согласования (Карусель)
    if not SaveState(sender_id, "164698c0-9f5a-4cab-9a5a-29c8591739b6", service_data_bot_need, data, carousel_id): #proc11fe0cd9823f4515909ff0df1baccf1a
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return

    number_parts = 1;
    temp = service_data_bot_need.get("number_parts11fe0cd9823f4515909ff0df1baccf1a")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_corteges11fe0cd9823f4515909ff0df1baccf1a(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_parts11fe0cd9823f4515909ff0df1baccf1a":number_parts})
        if not SaveState(sender_id, "39419e6c-491b-41e3-ac0a-5c7ff3252c43", service_data_bot_need, data, carousel_id): #proc_expect_comand_user11fe0cd9823f4515909ff0df1baccf1a
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    elif result_list == "1":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия
    return

def proc_get_list_corteges11fe0cd9823f4515909ff0df1baccf1a(sender_id, data, carousel_id)
    #Мои согласования (получение списка кортежей)



def proc_expect_comand_user11fe0cd9823f4515909ff0df1baccf1a(sender_id, message, data, service_data_bot_need, carousel_id)
    #Мои согласования (обработчик выбора пользователя из карусели или команды под ней)
    id = GetTextCommand(message)
    if id == "cancel":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_parts11fe0cd9823f4515909ff0df1baccf1a")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_parts11fe0cd9823f4515909ff0df1baccf1a": number_parts + 1})
        proc11fe0cd9823f4515909ff0df1baccf1a(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        procab414b6fa89b423faf796cc966fe1af8(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод элемента карусели (Вывод элемента карусели)
        procb591e68ff608423c982dd67e280ab1d4(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусели (Вывод команд для выбранного элемента карусели)
    return

def procab414b6fa89b423faf796cc966fe1af8(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод элемента карусели

    detail_view = proc_get_user_detail_view_by_idab414b6fa89b423faf796cc966fe1af8(sender_id, carousel_id, data)
    viber.send_messages(sender_id, TextMessage(text=detail_view))
    return

def proc_get_user_detail_view_by_idab414b6fa89b423faf796cc966fe1af8(sender_id, element_id, data)
    #Вывод элемента карусели (функция получения детального представления выбранного элемента карусели)


def procb591e68ff608423c982dd67e280ab1d4(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (команды элемента карусели)
    if not SaveState(sender_id, "4d1f9b8c-6b35-4a79-912b-94ed68ab51fd", service_data_bot_need, data, carousel_id): #procb591e68ff608423c982dd67e280ab1d4
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    buttons = []
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons})
    if not SaveState(sender_id, "80cd33c5-d01e-477d-8eb8-84907eac7b2d", service_data_bot_need, data, carousel_id): #proc_expect_user_button_clickb591e68ff608423c982dd67e280ab1d4
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_clickb591e68ff608423c982dd67e280ab1d4(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (Обработчик выбора из подчиненных команд элемента карусели)
    command = GetTextCommand(message)
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proce73308888cc644eea230a5c12d47ffd3(sender_id, message, data, service_data_bot_need, carousel_id):
    #Последние сообщения (Карусель)
    if not SaveState(sender_id, "03300c89-8ba0-4d5c-a441-9418d659dbe2", service_data_bot_need, data, carousel_id): #proce73308888cc644eea230a5c12d47ffd3
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return

    number_parts = 1;
    temp = service_data_bot_need.get("number_partse73308888cc644eea230a5c12d47ffd3")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_cortegese73308888cc644eea230a5c12d47ffd3(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_partse73308888cc644eea230a5c12d47ffd3":number_parts})
        if not SaveState(sender_id, "53103250-3e13-489f-8cf1-d9bd7113bea6", service_data_bot_need, data, carousel_id): #proc_expect_comand_usere73308888cc644eea230a5c12d47ffd3
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    elif result_list == "1":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия
    return

def proc_get_list_cortegese73308888cc644eea230a5c12d47ffd3(sender_id, data, carousel_id)
    #Последние сообщения (получение списка кортежей)



def proc_expect_comand_usere73308888cc644eea230a5c12d47ffd3(sender_id, message, data, service_data_bot_need, carousel_id)
    #Последние сообщения (обработчик выбора пользователя из карусели или команды под ней)
    id = GetTextCommand(message)
    if id == "cancel":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_partse73308888cc644eea230a5c12d47ffd3")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_partse73308888cc644eea230a5c12d47ffd3": number_parts + 1})
        proce73308888cc644eea230a5c12d47ffd3(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        procea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод элемента карусели (Вывод элемента карусели)
        proc317d123326fa48198178c3fa479cd7cc(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусели (Вывод команд для выбранного элемента карусели)
    return

def proc317d123326fa48198178c3fa479cd7cc(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (команды элемента карусели)
    if not SaveState(sender_id, "8aecd9e2-3789-465d-8178-cc77d64c70dd", service_data_bot_need, data, carousel_id): #proc317d123326fa48198178c3fa479cd7cc
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    buttons = []
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons})
    if not SaveState(sender_id, "4663ac84-2d63-4514-8fff-348812aa59e3", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click317d123326fa48198178c3fa479cd7cc
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click317d123326fa48198178c3fa479cd7cc(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (Обработчик выбора из подчиненных команд элемента карусели)
    command = GetTextCommand(message)
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proc5160f46d71b8466a8b28db1bf17d5392(sender_id, message, data, service_data_bot_need, carousel_id):
    #Обращения для подтверждения (Карусель)
    if not SaveState(sender_id, "8c5ccbee-cdf5-4021-815b-2f1dd9d0846d", service_data_bot_need, data, carousel_id): #proc5160f46d71b8466a8b28db1bf17d5392
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return

    number_parts = 1;
    temp = service_data_bot_need.get("number_parts5160f46d71b8466a8b28db1bf17d5392")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_corteges5160f46d71b8466a8b28db1bf17d5392(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_parts5160f46d71b8466a8b28db1bf17d5392":number_parts})
        if not SaveState(sender_id, "3633bd59-2f6e-486b-a50d-e46630b4e52a", service_data_bot_need, data, carousel_id): #proc_expect_comand_user5160f46d71b8466a8b28db1bf17d5392
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    elif result_list == "1":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия
    return

def proc_get_list_corteges5160f46d71b8466a8b28db1bf17d5392(sender_id, data, carousel_id)
    #Обращения для подтверждения (получение списка кортежей)



def proc_expect_comand_user5160f46d71b8466a8b28db1bf17d5392(sender_id, message, data, service_data_bot_need, carousel_id)
    #Обращения для подтверждения (обработчик выбора пользователя из карусели или команды под ней)
    id = GetTextCommand(message)
    if id == "cancel":
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_parts5160f46d71b8466a8b28db1bf17d5392")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_parts5160f46d71b8466a8b28db1bf17d5392": number_parts + 1})
        proc5160f46d71b8466a8b28db1bf17d5392(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        procea557c1bbda64ec0a0c7ad3e4f493afc(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод элемента карусели (Вывод элемента карусели)
        procdae1f3640d8a4eb0aed3fc1b63e187aa(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусели (Вывод команд для выбранного элемента карусели)
    return

def procdae1f3640d8a4eb0aed3fc1b63e187aa(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (команды элемента карусели)
    if not SaveState(sender_id, "0e89a178-4a5e-45d5-bf1d-10137e238367", service_data_bot_need, data, carousel_id): #procdae1f3640d8a4eb0aed3fc1b63e187aa
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    buttons = []
    buttons.append({|
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "5ba6c9fd-cb21-4aa2-972c-4020574f3157",
        "Text": "Подтвердить" })
    buttons.append({|
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "3ec26f31-a5dd-4ff7-a95f-c7c612cf273a",
        "Text": "Отклонить" })
    buttons.append({|
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "42747c5a-b756-49b0-b830-bcf82d3dca9c",
        "Text": "Назад" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons})
    if not SaveState(sender_id, "45c35ed8-4a57-4a46-9611-7040c944b912", service_data_bot_need, data, carousel_id): #proc_expect_user_button_clickdae1f3640d8a4eb0aed3fc1b63e187aa
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_clickdae1f3640d8a4eb0aed3fc1b63e187aa(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусели (Обработчик выбора из подчиненных команд элемента карусели)
    command = GetTextCommand(message)
    if command == "5ba6c9fd-cb21-4aa2-972c-4020574f3157":
        proc5ba6c9fdcb214aa2972c4020574f3157(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить
    elif command == "3ec26f31-a5dd-4ff7-a95f-c7c612cf273a":
        proc3ec26f31a5dd4ff7a95fc7c612cf273a(sender_id, message, data, service_data_bot_need, carousel_id) #Отклонить
    elif command == "42747c5a-b756-49b0-b830-bcf82d3dca9c":
        proc42747c5ab75649b0b830bcf82d3dca9c(sender_id, message, data, service_data_bot_need, carousel_id) #Назад
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proc5ba6c9fdcb214aa2972c4020574f3157(sender_id, message, data, service_data_bot_need, carousel_id):
    #Подтвердить (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function5ba6c9fdcb214aa2972c4020574f3157(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_rating":
        proca22a380f1e104600808c465bd6ab3777(sender_id, message, data, service_data_bot_need, carousel_id) #Указать оценку обязательно
    elif result_programm_select == "rating_exist":
        procd454043806d1401f87b5ab49f4142f18(sender_id, message, data, service_data_bot_need, carousel_id) #Указать оценку по желанию
    return

def proc_function5ba6c9fdcb214aa2972c4020574f3157(sender_id, message, data, service_data_bot_need, carousel_id):
    #Подтвердить (функция программного выбора)


def proca22a380f1e104600808c465bd6ab3777(sender_id, message, data, service_data_bot_need, carousel_id):
    #Указать оценку обязательно (выбор из подчиненных команд)
    if not SaveState(sender_id, "6debe1ee-7ed2-4089-90e8-bf5c0197a0b7", service_data_bot_need, data, carousel_id): #proca22a380f1e104600808c465bd6ab3777
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Оцените выполнение обращения"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "f78d8071-4386-4b3f-8cd2-91a0d503f281",
        "Text": "1" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "70a014c3-ff72-418a-bb1b-94326c535cd6",
        "Text": "2" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "1c315c3c-887a-489b-9552-2e1316af7b35",
        "Text": "3" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "12a983c4-1023-40aa-85d7-d182b9a7e2c5",
        "Text": "4" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "619fd5ff-8484-46fd-8f22-17bb68bc6a3b",
        "Text": "5" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "e6d53aa2-210b-4ed3-8e9f-5e6cea9bc777",
        "Text": "Отменить" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons": buttons}))
    if not SaveState(sender_id, "e7021b66-da11-43d1-a5fb-06b43e2dd39b", service_data_bot_need, data, carousel_id): #proc_expect_user_button_clicka22a380f1e104600808c465bd6ab3777
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_clicka22a380f1e104600808c465bd6ab3777(sender_id, message, data, service_data_bot_need, carousel_id):
    #Указать оценку обязательно (Обработчик выбора из подчиненных команд)
    command = GetTextCommand(message)
    if command == "f78d8071-4386-4b3f-8cd2-91a0d503f281":
        procf78d807143864b3f8cd291a0d503f281(sender_id, message, data, service_data_bot_need, carousel_id) #1
    elif command == "70a014c3-ff72-418a-bb1b-94326c535cd6":
        proc70a014c3ff72418abb1b94326c535cd6(sender_id, message, data, service_data_bot_need, carousel_id) #2
    elif command == "1c315c3c-887a-489b-9552-2e1316af7b35":
        proc1c315c3c887a489b95522e1316af7b35(sender_id, message, data, service_data_bot_need, carousel_id) #3
    elif command == "12a983c4-1023-40aa-85d7-d182b9a7e2c5":
        proc12a983c4102340aa85d7d182b9a7e2c5(sender_id, message, data, service_data_bot_need, carousel_id) #4
    elif command == "619fd5ff-8484-46fd-8f22-17bb68bc6a3b":
        proc619fd5ff848446fd8f2217bb68bc6a3b(sender_id, message, data, service_data_bot_need, carousel_id) #5
    elif command == "e6d53aa2-210b-4ed3-8e9f-5e6cea9bc777":
        proce6d53aa2210b4ed38e9f5e6cea9bc777(sender_id, message, data, service_data_bot_need, carousel_id) #Отменить
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def procf78d807143864b3f8cd291a0d503f281(sender_id, message, data, service_data_bot_need, carousel_id):
    #1 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_functionf78d807143864b3f8cd291a0d503f281(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_functionf78d807143864b3f8cd291a0d503f281(sender_id, message, data, service_data_bot_need, carousel_id):
    #1 (функция программного выбора)


def procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id):
    #Подтвердить и записать (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_functionf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "1":
        proc5b1b53252b954c049b947a4d5d5e1a52(sender_id, message, data, service_data_bot_need, carousel_id) #Запись удачная
    elif result_programm_select == "2":
        proc268053bdfcb14b06aacdc9c1d1131c63(sender_id, message, data, service_data_bot_need, carousel_id) #Запись неудачная
    return

def proc_functionf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id):
    #Подтвердить и записать (функция программного выбора)


def proc5b1b53252b954c049b947a4d5d5e1a52(sender_id, message, data, service_data_bot_need, carousel_id):
    #Запись удачная
    viber.send_messages(sender_id, TextMessage(text="Обращение подтверждено"))
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

def proc268053bdfcb14b06aacdc9c1d1131c63(sender_id, message, data, service_data_bot_need, carousel_id):
    #Запись неудачная
    viber.send_messages(sender_id, TextMessage(text="Не удалось подвердить обращение"))
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

def procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id):
    #Указать комментарий (выбор по результатам ввода с клавиатуры)
    viber.send_messages(sender_id, TextMessage(text="Укажите комментарий"))
    if not SaveState(sender_id, "3286e1d8-2d08-4cfa-b36f-989cece795b7", service_data_bot_need, data, carousel_id): #proc_function_expect_userd2aeca9275214a6caa98de3001dd081f
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_function_expect_userd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id):
    if not isinstance(data, dict):
        data = {}
    text = GetTextCommand(message)
    result_programm_select = proc_functiond2aeca9275214a6caa98de3001dd081f(sender_id, text, data, carousel_id)
    if result_programm_select == "comment_not_empty":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    elif result_programm_select == "comment_empty":
        procc325018b7fe6466d919422e0ec4b00e5(sender_id, message, data, service_data_bot_need, carousel_id) #Пустой комментарий

def proc_functiond2aeca9275214a6caa98de3001dd081f(sender_id, text, data, carousel_id):
    #Указать комментарий (функция обработки выбора с клавиатуры)


def procc325018b7fe6466d919422e0ec4b00e5(sender_id, message, data, service_data_bot_need, carousel_id):
    #Пустой комментарий
    viber.send_messages(sender_id, TextMessage(text="Комментарий не должен быть пустым"))
    procdae1f3640d8a4eb0aed3fc1b63e187aa(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Команды карусели
    return

def proc70a014c3ff72418abb1b94326c535cd6(sender_id, message, data, service_data_bot_need, carousel_id):
    #2 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function70a014c3ff72418abb1b94326c535cd6(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function70a014c3ff72418abb1b94326c535cd6(sender_id, message, data, service_data_bot_need, carousel_id):
    #2 (функция программного выбора)


def proc1c315c3c887a489b95522e1316af7b35(sender_id, message, data, service_data_bot_need, carousel_id):
    #3 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function1c315c3c887a489b95522e1316af7b35(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function1c315c3c887a489b95522e1316af7b35(sender_id, message, data, service_data_bot_need, carousel_id):
    #3 (функция программного выбора)


def proc12a983c4102340aa85d7d182b9a7e2c5(sender_id, message, data, service_data_bot_need, carousel_id):
    #4 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function12a983c4102340aa85d7d182b9a7e2c5(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function12a983c4102340aa85d7d182b9a7e2c5(sender_id, message, data, service_data_bot_need, carousel_id):
    #4 (функция программного выбора)


def proc619fd5ff848446fd8f2217bb68bc6a3b(sender_id, message, data, service_data_bot_need, carousel_id):
    #5 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function619fd5ff848446fd8f2217bb68bc6a3b(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function619fd5ff848446fd8f2217bb68bc6a3b(sender_id, message, data, service_data_bot_need, carousel_id):
    #5 (функция программного выбора)


def proce6d53aa2210b4ed38e9f5e6cea9bc777(sender_id, message, data, service_data_bot_need, carousel_id):
    #Отменить
    viber.send_messages(sender_id, TextMessage(text="Подтверждение не выполнено"))
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

def procd454043806d1401f87b5ab49f4142f18(sender_id, message, data, service_data_bot_need, carousel_id):
    #Указать оценку по желанию (выбор из подчиненных команд)
    if not SaveState(sender_id, "fd05d793-5172-4a34-b5ee-da1a28b12006", service_data_bot_need, data, carousel_id): #procd454043806d1401f87b5ab49f4142f18
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Оцените выполнение обращения"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "8fe80170-3cea-47eb-8291-e37e9d4751aa",
        "Text": "1" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "15a311c3-a872-416e-a2f4-9b8f41712bad",
        "Text": "2" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "b63c3343-a6f0-42f9-bd5f-575fdbe43d20",
        "Text": "3" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "8ce4471c-310e-49c4-bad6-2b82996d23e8",
        "Text": "4" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "ea302a5c-ac3d-477b-8fd2-68a66fb56264",
        "Text": "5" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "45188a2f-e76f-463d-a930-4c5a53876d70",
        "Text": "Пропустить" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons": buttons}))
    if not SaveState(sender_id, "4b420e79-b97f-413d-9943-f1f546b5a5c8", service_data_bot_need, data, carousel_id): #proc_expect_user_button_clickd454043806d1401f87b5ab49f4142f18
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_clickd454043806d1401f87b5ab49f4142f18(sender_id, message, data, service_data_bot_need, carousel_id):
    #Указать оценку по желанию (Обработчик выбора из подчиненных команд)
    command = GetTextCommand(message)
    if command == "8fe80170-3cea-47eb-8291-e37e9d4751aa":
        proc8fe801703cea47eb8291e37e9d4751aa(sender_id, message, data, service_data_bot_need, carousel_id) #1
    elif command == "15a311c3-a872-416e-a2f4-9b8f41712bad":
        proc15a311c3a872416ea2f49b8f41712bad(sender_id, message, data, service_data_bot_need, carousel_id) #2
    elif command == "b63c3343-a6f0-42f9-bd5f-575fdbe43d20":
        procb63c3343a6f042f9bd5f575fdbe43d20(sender_id, message, data, service_data_bot_need, carousel_id) #3
    elif command == "8ce4471c-310e-49c4-bad6-2b82996d23e8":
        proc8ce4471c310e49c4bad62b82996d23e8(sender_id, message, data, service_data_bot_need, carousel_id) #4
    elif command == "ea302a5c-ac3d-477b-8fd2-68a66fb56264":
        procea302a5cac3d477b8fd268a66fb56264(sender_id, message, data, service_data_bot_need, carousel_id) #5
    elif command == "45188a2f-e76f-463d-a930-4c5a53876d70":
        proc45188a2fe76f463da9304c5a53876d70(sender_id, message, data, service_data_bot_need, carousel_id) #Пропустить
    else:
        proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор действия

def proc8fe801703cea47eb8291e37e9d4751aa(sender_id, message, data, service_data_bot_need, carousel_id):
    #1 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function8fe801703cea47eb8291e37e9d4751aa(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function8fe801703cea47eb8291e37e9d4751aa(sender_id, message, data, service_data_bot_need, carousel_id):
    #1 (функция программного выбора)


def proc15a311c3a872416ea2f49b8f41712bad(sender_id, message, data, service_data_bot_need, carousel_id):
    #2 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function15a311c3a872416ea2f49b8f41712bad(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function15a311c3a872416ea2f49b8f41712bad(sender_id, message, data, service_data_bot_need, carousel_id):
    #2 (функция программного выбора)


def procb63c3343a6f042f9bd5f575fdbe43d20(sender_id, message, data, service_data_bot_need, carousel_id):
    #3 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_functionb63c3343a6f042f9bd5f575fdbe43d20(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_functionb63c3343a6f042f9bd5f575fdbe43d20(sender_id, message, data, service_data_bot_need, carousel_id):
    #3 (функция программного выбора)


def proc8ce4471c310e49c4bad62b82996d23e8(sender_id, message, data, service_data_bot_need, carousel_id):
    #4 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function8ce4471c310e49c4bad62b82996d23e8(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_function8ce4471c310e49c4bad62b82996d23e8(sender_id, message, data, service_data_bot_need, carousel_id):
    #4 (функция программного выбора)


def procea302a5cac3d477b8fd268a66fb56264(sender_id, message, data, service_data_bot_need, carousel_id):
    #5 (программный выбор)
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_functionea302a5cac3d477b8fd268a66fb56264(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "need_comment":
        procd2aeca9275214a6caa98de3001dd081f(sender_id, message, data, service_data_bot_need, carousel_id) #Указать комментарий
    elif result_programm_select == "no_need":
        procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Подтвердить и записать
    return

def proc_functionea302a5cac3d477b8fd268a66fb56264(sender_id, message, data, service_data_bot_need, carousel_id):
    #5 (функция программного выбора)


def proc45188a2fe76f463da9304c5a53876d70(sender_id, message, data, service_data_bot_need, carousel_id):
    #Пропустить
    procf6e8c44744ad474b8192b993d45f4ce5(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Подтвердить и записать
    return

def proc3ec26f31a5dd4ff7a95fc7c612cf273a(sender_id, message, data, service_data_bot_need, carousel_id):
    #Отклонить (выбор по результатам ввода с клавиатуры)
    viber.send_messages(sender_id, TextMessage(text="Введите комментарий"))
    if not SaveState(sender_id, "04a7d0fa-4dda-43e6-a867-c7c0e88da724", service_data_bot_need, data, carousel_id): #proc_function_expect_user3ec26f31a5dd4ff7a95fc7c612cf273a
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_function_expect_user3ec26f31a5dd4ff7a95fc7c612cf273a(sender_id, message, data, service_data_bot_need, carousel_id):
    if not isinstance(data, dict):
        data = {}
    text = GetTextCommand(message)
    result_programm_select = proc_function3ec26f31a5dd4ff7a95fc7c612cf273a(sender_id, text, data, carousel_id)
    if result_programm_select == "1":
        proc3acf9e3b54a5487191e24a5de6948277(sender_id, message, data, service_data_bot_need, carousel_id) #Отклонено успешно
    elif result_programm_select == "2":
        proccfbbb503f7b94287b6219ec07cbe0afa(sender_id, message, data, service_data_bot_need, carousel_id) #Не удалось отклонить

def proc_function3ec26f31a5dd4ff7a95fc7c612cf273a(sender_id, text, data, carousel_id):
    #Отклонить (функция обработки выбора с клавиатуры)


def proc3acf9e3b54a5487191e24a5de6948277(sender_id, message, data, service_data_bot_need, carousel_id):
    #Отклонено успешно
    viber.send_messages(sender_id, TextMessage(text="Отклонено успешно"))
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

def proccfbbb503f7b94287b6219ec07cbe0afa(sender_id, message, data, service_data_bot_need, carousel_id):
    #Не удалось отклонить
    viber.send_messages(sender_id, TextMessage(text="Не удалось отклонить обращение"))
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

def proc42747c5ab75649b0b830bcf82d3dca9c(sender_id, message, data, service_data_bot_need, carousel_id):
    #Назад
    proc095761bb67d8455bbf094e32d0e8dc4f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Выбор действия
    return

list_procs = {}
list_procs.update( { '42e116a3-1716-47af-95a4-27feea6b8678': proc_function_expect_user1b68be2d5a9a4d06adb59b874e1673ea} )
list_procs.update( { '1571b3a5-ce91-474f-b189-2987ba84c8d8': proc095761bb67d8455bbf094e32d0e8dc4f} )
list_procs.update( { '3350e75b-c2b2-4771-a4ae-2bde1f591295': proc_expect_user_button_click095761bb67d8455bbf094e32d0e8dc4f} )
list_procs.update( { '6fd6a6df-765d-44e4-b2cf-04fee4be35d2': procf6829c8beb464c618ab63bd31f6bc879} )
list_procs.update( { '272935d4-48b8-405b-96ab-fdf65d9c133d': proc_expect_comand_userf6829c8beb464c618ab63bd31f6bc879} )
list_procs.update( { '238a9170-e105-4bcf-872d-ba0f6194eb0c': proc17c11a9477c8493db93470bdbee77ffc} )
list_procs.update( { '41d299c9-5fee-4f00-b41f-1a6c53b8d555': proc_expect_user_button_click17c11a9477c8493db93470bdbee77ffc} )
list_procs.update( { '164698c0-9f5a-4cab-9a5a-29c8591739b6': proc11fe0cd9823f4515909ff0df1baccf1a} )
list_procs.update( { '39419e6c-491b-41e3-ac0a-5c7ff3252c43': proc_expect_comand_user11fe0cd9823f4515909ff0df1baccf1a} )
list_procs.update( { '4d1f9b8c-6b35-4a79-912b-94ed68ab51fd': procb591e68ff608423c982dd67e280ab1d4} )
list_procs.update( { '80cd33c5-d01e-477d-8eb8-84907eac7b2d': proc_expect_user_button_clickb591e68ff608423c982dd67e280ab1d4} )
list_procs.update( { '03300c89-8ba0-4d5c-a441-9418d659dbe2': proce73308888cc644eea230a5c12d47ffd3} )
list_procs.update( { '53103250-3e13-489f-8cf1-d9bd7113bea6': proc_expect_comand_usere73308888cc644eea230a5c12d47ffd3} )
list_procs.update( { '8aecd9e2-3789-465d-8178-cc77d64c70dd': proc317d123326fa48198178c3fa479cd7cc} )
list_procs.update( { '4663ac84-2d63-4514-8fff-348812aa59e3': proc_expect_user_button_click317d123326fa48198178c3fa479cd7cc} )
list_procs.update( { '8c5ccbee-cdf5-4021-815b-2f1dd9d0846d': proc5160f46d71b8466a8b28db1bf17d5392} )
list_procs.update( { '3633bd59-2f6e-486b-a50d-e46630b4e52a': proc_expect_comand_user5160f46d71b8466a8b28db1bf17d5392} )
list_procs.update( { '0e89a178-4a5e-45d5-bf1d-10137e238367': procdae1f3640d8a4eb0aed3fc1b63e187aa} )
list_procs.update( { '45c35ed8-4a57-4a46-9611-7040c944b912': proc_expect_user_button_clickdae1f3640d8a4eb0aed3fc1b63e187aa} )
list_procs.update( { '6debe1ee-7ed2-4089-90e8-bf5c0197a0b7': proca22a380f1e104600808c465bd6ab3777} )
list_procs.update( { 'e7021b66-da11-43d1-a5fb-06b43e2dd39b': proc_expect_user_button_clicka22a380f1e104600808c465bd6ab3777} )
list_procs.update( { '3286e1d8-2d08-4cfa-b36f-989cece795b7': proc_function_expect_userd2aeca9275214a6caa98de3001dd081f} )
list_procs.update( { 'fd05d793-5172-4a34-b5ee-da1a28b12006': procd454043806d1401f87b5ab49f4142f18} )
list_procs.update( { '4b420e79-b97f-413d-9943-f1f546b5a5c8': proc_expect_user_button_clickd454043806d1401f87b5ab49f4142f18} )
list_procs.update( { '04a7d0fa-4dda-43e6-a867-c7c0e88da724': proc_function_expect_user3ec26f31a5dd4ff7a95fc7c612cf273a} )

def GoToStateError(sender_id, message, state_id, data, data_user, carousel_id):
    GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)
    return

def GoToStateByID(sender_id, message, state_id, service_data_bot_need, data_user, carousel_id):
    procedure = list_procs.get(state_id)
    if not isinstance(service_data_bot_need, dict)
        service_data_bot_need = {}
    if not isinstance(data, dict)
            data_user = {}
    procedure(sender_id, message, data_user, service_data_bot_need, carousel_id)

    return

def GoToCurrentState(sender_id, message):
    try
        result_restore, state_id, data, data_user, carousel_id = RestoreState(sender_id)
        if result_restore:
            GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)   |
        else:
            viber.send_messages(sender_id, TextMessage(text=data))
            GoToStateError(sender_id, message, GetIdErrorState(), data, data_user, carousel_id)
    except:
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
    return

def SetHooksIfNeed():
    need_hook = False   |
    try:
        need_drop = False
        DATABASE_URL = os.environ['DATABASE_URL']
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Open a cursor to perform database operations
        cur = conn.cursor()
        cur.execute("select * from information_schema.tables where table_name=%s", ('data_hooks',))
        if(cur.rowcount == 0):
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE data_hooks (id serial PRIMARY KEY, state TEXT );")
            need_hook = True
        else:
            cur.execute("SELECT state FROM data_hooks")
            result_query = cur.fetchone()
            if(result_query == None):
                need_hook = True
            elif not result_query[0] == "1":
                need_hook = True
                need_drop = True
            else: #result_query[0] == "1":
                need_hook = False

        if need_hook:
            if need_drop:
                cur.execute("DELETE FROM data_hooks");
            viber = Api(BotConfiguration(
                name='Itilium-bot',
                avatar='http://site.com/avatar.jpg',
                auth_token=auth_token_out
                ))
            viber.unset_webhook()
            viber.set_webhook(request.url[0:len(r) - len("register")])

            cur.execute("INSERT INTO data_hooks (state) VALUES (%s)",
                  ("1",))
        conn.commit()
    except:
        return False, False
    finally:
        cur.close()
        conn.close()
    return True, need_hook

app = Flask(__name__)

@app.route('/',  methods=['GET'])
def IncomingGet():
    state, need_hook = SetHooksIfNeed()
    if state:
        if need_hook:
            return "Регистрация бота прошла успешно"
        else:
            return "Бот был зарегистрирован ранее"
    else:
        return "Ошибка при регистрации бота. Поробуйте вручную"

@app.route('/',  methods=['POST'])
def incoming():
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        sender_id = viber_request.sender.id
        message = viber_request.message

        GoToCurrentState(sender_id, message)

    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.sender.id, "Вы зарегистрированы")
    elif isinstance(viber_request, ViberFailedRequest):
        viber.send_messages(viber_request.sender.id, "Сообщение не отправлено")

    return Response(status=200)
