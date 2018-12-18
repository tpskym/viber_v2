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
    print("stack: SaveStateToPostgress")
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
    print("stack: RestoreStateFromPostgress")
    state = False
    is_error = False
    try:
        restore_ok = True
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
    except Exception as e:
        is_error = True
        restore_ok = False
        print("Error on restore data:" + e.args[0])
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
    print("stack: GetTextCommand")
    if (isinstance(message, str)):
        text = message
    elif (isinstance(message, TextMessage)):
        text = message.text
    else:
        text = message.text
    return text

def GetIsRegisteredUser(sender_id):
    return True

def GetIdErrorState():
    print("stack: GetIdErrorState")
    return "ba08f868-ea17-4d09-96e8-eb2b9d43be27" #Ошибка

def ShowCarousel(sender_id, result_list, number_parts):

    print("stack: ShowCarousel")
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
    print("stack: SaveState")
    if SaveStateToPostgress(sender_id, state_id, carousel_id, data_user, data):
        return True
    else:
        return False

def RestoreState(sender_id):
    print("stack: RestoreState")
    result_dict = RestoreStateFromPostgress(sender_id)
    if result_dict.get('state') == True:
         return (True, False ,result_dict.get('state_id'), result_dict.get('data'), result_dict.get('data_user'), result_dict.get('carousel_id'))
    else:
         return (False,  result_dict.get('error'), "", "", "", "")




def proce3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id):
    #Первое состояние (программный выбор)
    print("stack: proce3cafc7fe33b41c4b38c40b9d62a3e55")
    viber.send_messages(sender_id, TextMessage(text="Привет!"))
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_functione3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "1":
        procfc4a6135fb2443e8bcb7282f64002b44(sender_id, message, data, service_data_bot_need, carousel_id) #Состояние обработка ввода с клавиатуры
    return

def proc_functione3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id):
    #Первое состояние (функция программного выбора)
    print("stack: proc_functione3cafc7fe33b41c4b38c40b9d62a3e55")
    return "1"

def procfc4a6135fb2443e8bcb7282f64002b44(sender_id, message, data, service_data_bot_need, carousel_id):
    #Состояние обработка ввода с клавиатуры (выбор по результатам ввода с клавиатуры)
    print("stack: procfc4a6135fb2443e8bcb7282f64002b44")
    viber.send_messages(sender_id, TextMessage(text="Введите 1"))
    if not SaveState(sender_id, "c4a6135-fb24-43e8-bcb7-282f64002b44f", service_data_bot_need, data, carousel_id): #proc_function_expect_userfc4a6135fb2443e8bcb7282f64002b44
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_function_expect_userfc4a6135fb2443e8bcb7282f64002b44(sender_id, message, data, service_data_bot_need, carousel_id):
    # Выбор по результатам ввода с клавиатуры. Обработка ввота пользователя
    print("stack: proc_function_expect_userfc4a6135fb2443e8bcb7282f64002b44")
    if not isinstance(data, dict):
        data = {}
    text = GetTextCommand(message)
    result_programm_select = proc_functionfc4a6135fb2443e8bcb7282f64002b44(sender_id, text, data, carousel_id)
    if result_programm_select == "1":
        proc7cc31168f3d146afbf06b765d0e989d3(sender_id, message, data, service_data_bot_need, carousel_id) #Выбор из подчиненных команд
    elif result_programm_select == "2":
        procfc4a6135fb2443e8bcb7282f64002b44(sender_id, message, data, service_data_bot_need, carousel_id) #Состояние обработка ввода с клавиатуры

def proc_functionfc4a6135fb2443e8bcb7282f64002b44(sender_id, text, data, carousel_id):
    #Состояние обработка ввода с клавиатуры (функция обработки выбора с клавиатуры)
    print("stack: proc_functionfc4a6135fb2443e8bcb7282f64002b44")
    if text == "1":
        return "1"
    else:
        return "2"

def proc7cc31168f3d146afbf06b765d0e989d3(sender_id, message, data, service_data_bot_need, carousel_id):
    #Выбор из подчиненных команд (выбор из подчиненных команд)
    print("stack: proc7cc31168f3d146afbf06b765d0e989d3")
    if not SaveState(sender_id, "7cc31168-f3d1-46af-bf06-b765d0e989d3", service_data_bot_need, data, carousel_id): #proc7cc31168f3d146afbf06b765d0e989d3
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Выберите команду"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "8e6deb53-f558-452f-a2de-aa243228837f",
        "Text": "Переход Состояние обработка ввода с клавиатуры" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "0432458f-1b34-417a-a2cc-453722d74476",
        "Text": "Карусель 1 - короткая" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "fb122677-b907-4763-a0b8-3694f35fcab8",
        "Text": "Карусель 2 - длинная" })
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "cd6e33ce-0e12-42df-bf0b-3d4b21234ccb",
        "Text": "Карусель 3 - с ошибкой" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons": buttons}))
    if not SaveState(sender_id, "cc31168-f3d1-46af-bf06-b765d0e989d37", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click7cc31168f3d146afbf06b765d0e989d3
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click7cc31168f3d146afbf06b765d0e989d3(sender_id, message, data, service_data_bot_need, carousel_id):
    #Выбор из подчиненных команд (Обработчик выбора из подчиненных команд)
    print("stack: proc_expect_user_button_click7cc31168f3d146afbf06b765d0e989d3")
    command = GetTextCommand(message)
    if command == "8e6deb53-f558-452f-a2de-aa243228837f":
        proc8e6deb53f558452fa2deaa243228837f(sender_id, message, data, service_data_bot_need, carousel_id) #Переход Состояние обработка ввода с клавиатуры
    elif command == "0432458f-1b34-417a-a2cc-453722d74476":
        proc0432458f1b34417aa2cc453722d74476(sender_id, message, data, service_data_bot_need, carousel_id) #Карусель 1 - короткая
    elif command == "fb122677-b907-4763-a0b8-3694f35fcab8":
        procfb122677b9074763a0b83694f35fcab8(sender_id, message, data, service_data_bot_need, carousel_id) #Карусель 2 - длинная
    elif command == "cd6e33ce-0e12-42df-bf0b-3d4b21234ccb":
        proccd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, message, data, service_data_bot_need, carousel_id) #Карусель 3 - с ошибкой
    procba08f868ea174d0996e8eb2b9d43be27(sender_id, message, data, service_data_bot_need, carousel_id) #Ошибка

def proc8e6deb53f558452fa2deaa243228837f(sender_id, message, data, service_data_bot_need, carousel_id):
    #Переход Состояние обработка ввода с клавиатуры
    print("stack: proc8e6deb53f558452fa2deaa243228837f")
    viber.send_messages(sender_id, TextMessage(text="Вы перенаправлены на \"состояние обработка ввода с клавиатуры\""))
    procfc4a6135fb2443e8bcb7282f64002b44(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Состояние обработка ввода с клавиатуры
    return

def proc0432458f1b34417aa2cc453722d74476(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 1 - короткая (Карусель)
    print("stack: proc0432458f1b34417aa2cc453722d74476")
    if not SaveState(sender_id, "0432458f-1b34-417a-a2cc-453722d74476", service_data_bot_need, data, carousel_id): #proc0432458f1b34417aa2cc453722d74476
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Вы на состоянии карусель 1 короткая"))

    number_parts = 1;
    temp = service_data_bot_need.get("number_parts0432458f1b34417aa2cc453722d74476")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_corteges0432458f1b34417aa2cc453722d74476(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_parts0432458f1b34417aa2cc453722d74476":number_parts})
        if not SaveState(sender_id, "432458f-1b34-417a-a2cc-453722d744760", service_data_bot_need, data, carousel_id): #proc_expect_comand_user0432458f1b34417aa2cc453722d74476
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    return

def proc_get_list_corteges0432458f1b34417aa2cc453722d74476(sender_id, data, carousel_id):
    #Карусель 1 - короткая (получение списка кортежей)
    print("stack: proc_get_list_corteges0432458f1b34417aa2cc453722d74476")
    return [("ID1","ID1Title","ID1DetailText"),("ID2","ID2Title","ID2DetailText"),("ID3","ID3Title","ID3DetailText")]


def proc_expect_comand_user0432458f1b34417aa2cc453722d74476(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 1 - короткая (обработчик выбора пользователя из карусели или команды под ней)
    print("stack: proc_expect_comand_user0432458f1b34417aa2cc453722d74476")
    id = GetTextCommand(message)
    if id == "cancel":
        proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Цикл окончен(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_parts0432458f1b34417aa2cc453722d74476")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_parts0432458f1b34417aa2cc453722d74476": number_parts + 1})
        proc0432458f1b34417aa2cc453722d74476(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        proc73c303a0ee5c49b78ded86688f87857a(sender_id, message, data, service_data_bot_need, carousel_id) #Обработчик вывода карусель 1 (Вывод элемента карусели)
        proc98c4ca3dfc2f4acdbf2f4efd2b21b7e0(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусель 1 (Вывод команд для выбранного элемента карусели)
    return

def proc73c303a0ee5c49b78ded86688f87857a(sender_id, message, data, service_data_bot_need, carousel_id):
    #Обработчик вывода карусель 1
    print("stack: proc73c303a0ee5c49b78ded86688f87857a")
    viber.send_messages(sender_id, TextMessage(text="Вывод элемента карусели"))

    detail_view = proc_get_user_detail_view_by_id73c303a0ee5c49b78ded86688f87857a(sender_id, carousel_id, data)
    viber.send_messages(sender_id, TextMessage(text=detail_view))
    return

def proc_get_user_detail_view_by_id73c303a0ee5c49b78ded86688f87857a(sender_id, element_id, data):
    #Обработчик вывода карусель 1 (функция получения детального представления выбранного элемента карусели)
    print("stack: proc_get_user_detail_view_by_id73c303a0ee5c49b78ded86688f87857a")
    data.update({'testdata1':"123"})
    return sender_id + ' ' + element_id

def proc98c4ca3dfc2f4acdbf2f4efd2b21b7e0(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 1 (команды элемента карусели)
    print("stack: proc98c4ca3dfc2f4acdbf2f4efd2b21b7e0")
    if not SaveState(sender_id, "98c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e0", service_data_bot_need, data, carousel_id): #proc98c4ca3dfc2f4acdbf2f4efd2b21b7e0
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Список команд карусели 1"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "7706f046-b68a-432e-bc55-74f3fc0344e5",
        "Text": "Вывод дополнительных данных" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons}))
    if not SaveState(sender_id, "8c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e09", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click98c4ca3dfc2f4acdbf2f4efd2b21b7e0
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click98c4ca3dfc2f4acdbf2f4efd2b21b7e0(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 1 (Обработчик выбора из подчиненных команд элемента карусели)
    print("stack: proc_expect_user_button_click98c4ca3dfc2f4acdbf2f4efd2b21b7e0")
    command = GetTextCommand(message)
    if command == "7706f046-b68a-432e-bc55-74f3fc0344e5":
        proc7706f046b68a432ebc5574f3fc0344e5(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод дополнительных данных
    procba08f868ea174d0996e8eb2b9d43be27(sender_id, message, data, service_data_bot_need, carousel_id) #Ошибка

def proc7706f046b68a432ebc5574f3fc0344e5(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод дополнительных данных (программный выбор)
    print("stack: proc7706f046b68a432ebc5574f3fc0344e5")
    viber.send_messages(sender_id, TextMessage(text="Вывод дополнительных команд"))
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function7706f046b68a432ebc5574f3fc0344e5(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "1":
        proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Цикл окончен
    return

def proc_function7706f046b68a432ebc5574f3fc0344e5(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод дополнительных данных (функция программного выбора)
    print("stack: proc_function7706f046b68a432ebc5574f3fc0344e5")
    viber.send_messages(sender_id, TextMessage(text=carousel_id + data.get('testdata1')))
    return "1"

def procfb122677b9074763a0b83694f35fcab8(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 2 - длинная (Карусель)
    print("stack: procfb122677b9074763a0b83694f35fcab8")
    if not SaveState(sender_id, "fb122677-b907-4763-a0b8-3694f35fcab8", service_data_bot_need, data, carousel_id): #procfb122677b9074763a0b83694f35fcab8
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Вы на состоянии карусель 2 длинная"))

    number_parts = 1;
    temp = service_data_bot_need.get("number_partsfb122677b9074763a0b83694f35fcab8")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_cortegesfb122677b9074763a0b83694f35fcab8(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_partsfb122677b9074763a0b83694f35fcab8":number_parts})
        if not SaveState(sender_id, "b122677-b907-4763-a0b8-3694f35fcab8f", service_data_bot_need, data, carousel_id): #proc_expect_comand_userfb122677b9074763a0b83694f35fcab8
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    return

def proc_get_list_cortegesfb122677b9074763a0b83694f35fcab8(sender_id, data, carousel_id):
    #Карусель 2 - длинная (получение списка кортежей)
    print("stack: proc_get_list_cortegesfb122677b9074763a0b83694f35fcab8")
    list = []
    for i in range(1, 100):
        cortege = ("ID" + str(i),"Title" + str(i) ,"DetailText" + str(i))
        list.append(cortege)
    return list


def proc_expect_comand_userfb122677b9074763a0b83694f35fcab8(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 2 - длинная (обработчик выбора пользователя из карусели или команды под ней)
    print("stack: proc_expect_comand_userfb122677b9074763a0b83694f35fcab8")
    id = GetTextCommand(message)
    if id == "cancel":
        proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Цикл окончен(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_partsfb122677b9074763a0b83694f35fcab8")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_partsfb122677b9074763a0b83694f35fcab8": number_parts + 1})
        procfb122677b9074763a0b83694f35fcab8(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        proc73c303a0ee5c49b78ded86688f87857a(sender_id, message, data, service_data_bot_need, carousel_id) #Обработчик вывода карусель 1 (Вывод элемента карусели)
        proc42a2f751ca6240a8b12e3f62ad73cb46(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусель 2 (Вывод команд для выбранного элемента карусели)
    return

def proc42a2f751ca6240a8b12e3f62ad73cb46(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 2 (команды элемента карусели)
    print("stack: proc42a2f751ca6240a8b12e3f62ad73cb46")
    if not SaveState(sender_id, "42a2f751-ca62-40a8-b12e-3f62ad73cb46", service_data_bot_need, data, carousel_id): #proc42a2f751ca6240a8b12e3f62ad73cb46
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Команды карусели 2 - длинной"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "54ab8048-6210-439e-a98f-79034ade1265",
        "Text": "Вывод выбранного в карусели 2" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons}))
    if not SaveState(sender_id, "2a2f751-ca62-40a8-b12e-3f62ad73cb464", service_data_bot_need, data, carousel_id): #proc_expect_user_button_click42a2f751ca6240a8b12e3f62ad73cb46
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_click42a2f751ca6240a8b12e3f62ad73cb46(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 2 (Обработчик выбора из подчиненных команд элемента карусели)
    print("stack: proc_expect_user_button_click42a2f751ca6240a8b12e3f62ad73cb46")
    command = GetTextCommand(message)
    if command == "54ab8048-6210-439e-a98f-79034ade1265":
        proc54ab80486210439ea98f79034ade1265(sender_id, message, data, service_data_bot_need, carousel_id) #Вывод выбранного в карусели 2
    procba08f868ea174d0996e8eb2b9d43be27(sender_id, message, data, service_data_bot_need, carousel_id) #Ошибка

def proc54ab80486210439ea98f79034ade1265(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод выбранного в карусели 2 (программный выбор)
    print("stack: proc54ab80486210439ea98f79034ade1265")
    viber.send_messages(sender_id, TextMessage(text="Вывод выбранного в карусели 2"))
    if not isinstance(data, dict):
        data = {}
    result_programm_select = proc_function54ab80486210439ea98f79034ade1265(sender_id, message, data, service_data_bot_need, carousel_id)
    if result_programm_select == "1":
        proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Цикл окончен
    return

def proc_function54ab80486210439ea98f79034ade1265(sender_id, message, data, service_data_bot_need, carousel_id):
    #Вывод выбранного в карусели 2 (функция программного выбора)
    print("stack: proc_function54ab80486210439ea98f79034ade1265")
    viber.send_messages(sender_id, TextMessage(text=carousel_id + data.get('testdata1')))
    return "1"

def proccd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 3 - с ошибкой (Карусель)
    print("stack: proccd6e33ce0e1242dfbf0b3d4b21234ccb")
    if not SaveState(sender_id, "cd6e33ce-0e12-42df-bf0b-3d4b21234ccb", service_data_bot_need, data, carousel_id): #proccd6e33ce0e1242dfbf0b3d4b21234ccb
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Вы на состоянии карусель 3 с ошибкой"))

    number_parts = 1;
    temp = service_data_bot_need.get("number_partscd6e33ce0e1242dfbf0b3d4b21234ccb")
    if not temp == None:
        number_parts = temp
    result_list = proc_get_list_cortegescd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, data, carousel_id)
    if isinstance(result_list, list):

        ShowCarousel(sender_id, result_list, number_parts)
        service_data_bot_need.update({"number_partscd6e33ce0e1242dfbf0b3d4b21234ccb":number_parts})
        if not SaveState(sender_id, "d6e33ce-0e12-42df-bf0b-3d4b21234ccbc", service_data_bot_need, data, carousel_id): #proc_expect_comand_usercd6e33ce0e1242dfbf0b3d4b21234ccb
            viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
            GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
            return
    elif result_list == "error":
        proc96cb68c07f0a44f1a585e5965c1fc8da(sender_id, message, data, service_data_bot_need, carousel_id) #Обработка ошибки карусель 3
    return

def proc_get_list_cortegescd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, data, carousel_id):
    #Карусель 3 - с ошибкой (получение списка кортежей)
    print("stack: proc_get_list_cortegescd6e33ce0e1242dfbf0b3d4b21234ccb")
    return "error"


def proc_expect_comand_usercd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, message, data, service_data_bot_need, carousel_id):
    #Карусель 3 - с ошибкой (обработчик выбора пользователя из карусели или команды под ней)
    print("stack: proc_expect_comand_usercd6e33ce0e1242dfbf0b3d4b21234ccb")
    id = GetTextCommand(message)
    if id == "cancel":
        proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Цикл окончен(команда "Отменить")
    elif id == "more_data":

        number_parts = 1
        temp = service_data_bot_need.get("number_partscd6e33ce0e1242dfbf0b3d4b21234ccb")
        if not temp == None:
            number_parts = temp
        service_data_bot_need.update({"number_partscd6e33ce0e1242dfbf0b3d4b21234ccb": number_parts + 1})
        proccd6e33ce0e1242dfbf0b3d4b21234ccb(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на вывод дополнительных непоместившихся элементов
    else:
        carousel_id = id
        proc73c303a0ee5c49b78ded86688f87857a(sender_id, message, data, service_data_bot_need, carousel_id) #Обработчик вывода карусель 1 (Вывод элемента карусели)
        proce4e000559b82453e97ee1fb091b22087(sender_id, message, data, service_data_bot_need, carousel_id) #Команды карусель 3 (Вывод команд для выбранного элемента карусели)
    return

def proce4e000559b82453e97ee1fb091b22087(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 3 (команды элемента карусели)
    print("stack: proce4e000559b82453e97ee1fb091b22087")
    if not SaveState(sender_id, "e4e00055-9b82-453e-97ee-1fb091b22087", service_data_bot_need, data, carousel_id): #proce4e000559b82453e97ee1fb091b22087
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    viber.send_messages(sender_id, TextMessage(text="Команды карусели 3 - с ошибкой"))
    buttons = []
    buttons.append({
        "Columns": 6,
        "Rows": 1,
        "ActionBody": "a9fa2734-6a2c-4eeb-8a14-105ad7c7c700",
        "Text": "Команда  карусели 3 с ошибкой" })
    viber.send_messages(sender_id, KeyboardMessage(min_api_version=4, keyboard={"InputFieldState": "hidden", "Type": "keyboard", "Buttons":buttons}))
    if not SaveState(sender_id, "4e00055-9b82-453e-97ee-1fb091b22087e", service_data_bot_need, data, carousel_id): #proc_expect_user_button_clicke4e000559b82453e97ee1fb091b22087
        viber.send_messages(sender_id, TextMessage(text="ERROR SAVE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
        return
    return

def proc_expect_user_button_clicke4e000559b82453e97ee1fb091b22087(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команды карусель 3 (Обработчик выбора из подчиненных команд элемента карусели)
    print("stack: proc_expect_user_button_clicke4e000559b82453e97ee1fb091b22087")
    command = GetTextCommand(message)
    if command == "a9fa2734-6a2c-4eeb-8a14-105ad7c7c700":
        proca9fa27346a2c4eeb8a14105ad7c7c700(sender_id, message, data, service_data_bot_need, carousel_id) #Команда  карусели 3 с ошибкой
    procba08f868ea174d0996e8eb2b9d43be27(sender_id, message, data, service_data_bot_need, carousel_id) #Ошибка

def proca9fa27346a2c4eeb8a14105ad7c7c700(sender_id, message, data, service_data_bot_need, carousel_id):
    #Команда  карусели 3 с ошибкой
    print("stack: proca9fa27346a2c4eeb8a14105ad7c7c700")
    viber.send_messages(sender_id, TextMessage(text="Команда карусели 3 с ошибкой - сюда попатсть не должно"))
    proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Цикл окончен
    return

def proc96cb68c07f0a44f1a585e5965c1fc8da(sender_id, message, data, service_data_bot_need, carousel_id):
    #Обработка ошибки карусель 3
    print("stack: proc96cb68c07f0a44f1a585e5965c1fc8da")
    viber.send_messages(sender_id, TextMessage(text="Ошибка по карусели 3 - все так и должно быть!"))
    proce3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Первое состояние
    return

def procba08f868ea174d0996e8eb2b9d43be27(sender_id, message, data, service_data_bot_need, carousel_id):
    #Ошибка
    print("stack: procba08f868ea174d0996e8eb2b9d43be27")
    viber.send_messages(sender_id, TextMessage(text="Ошибка"))
    proce3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Первое состояние
    return

def proc6dbf09d6a753425e9da0d809dcc4049e(sender_id, message, data, service_data_bot_need, carousel_id):
    #Цикл окончен
    print("stack: proc6dbf09d6a753425e9da0d809dcc4049e")
    viber.send_messages(sender_id, TextMessage(text="Цикл окончен"))
    proce3cafc7fe33b41c4b38c40b9d62a3e55(sender_id, message, data, service_data_bot_need, carousel_id) #Переход на Первое состояние
    return

list_procs = {}
list_procs.update( { 'e3cafc7f-e33b-41c4-b38c-40b9d62a3e55': proce3cafc7fe33b41c4b38c40b9d62a3e55,'e3cafc7f-e33b-41c4-b38c-40b9d62a3e55without_registration': False} )
list_procs.update( { 'fc4a6135-fb24-43e8-bcb7-282f64002b44': procfc4a6135fb2443e8bcb7282f64002b44,'fc4a6135-fb24-43e8-bcb7-282f64002b44without_registration': False} )
list_procs.update( { 'c4a6135-fb24-43e8-bcb7-282f64002b44f': proc_function_expect_userfc4a6135fb2443e8bcb7282f64002b44,'fc4a6135-fb24-43e8-bcb7-282f64002b44without_registration': False} )
list_procs.update( { '7cc31168-f3d1-46af-bf06-b765d0e989d3': proc7cc31168f3d146afbf06b765d0e989d3,'7cc31168-f3d1-46af-bf06-b765d0e989d3without_registration': False} )
list_procs.update( { 'cc31168-f3d1-46af-bf06-b765d0e989d37': proc_expect_user_button_click7cc31168f3d146afbf06b765d0e989d3,'7cc31168-f3d1-46af-bf06-b765d0e989d3without_registration': False} )
list_procs.update( { '8e6deb53-f558-452f-a2de-aa243228837f': proc8e6deb53f558452fa2deaa243228837f,'8e6deb53-f558-452f-a2de-aa243228837fwithout_registration': False} )
list_procs.update( { '0432458f-1b34-417a-a2cc-453722d74476': proc0432458f1b34417aa2cc453722d74476,'0432458f-1b34-417a-a2cc-453722d74476without_registration': False} )
list_procs.update( { '432458f-1b34-417a-a2cc-453722d744760': proc_expect_comand_user0432458f1b34417aa2cc453722d74476,'0432458f-1b34-417a-a2cc-453722d74476without_registration': False} )
list_procs.update( { '73c303a0-ee5c-49b7-8ded-86688f87857a': proc73c303a0ee5c49b78ded86688f87857a,'73c303a0-ee5c-49b7-8ded-86688f87857awithout_registration': False} )
list_procs.update( { '98c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e0': proc98c4ca3dfc2f4acdbf2f4efd2b21b7e0,'98c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e0without_registration': False} )
list_procs.update( { '8c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e09': proc_expect_user_button_click98c4ca3dfc2f4acdbf2f4efd2b21b7e0,'98c4ca3d-fc2f-4acd-bf2f-4efd2b21b7e0without_registration': False} )
list_procs.update( { '7706f046-b68a-432e-bc55-74f3fc0344e5': proc7706f046b68a432ebc5574f3fc0344e5,'7706f046-b68a-432e-bc55-74f3fc0344e5without_registration': False} )
list_procs.update( { 'fb122677-b907-4763-a0b8-3694f35fcab8': procfb122677b9074763a0b83694f35fcab8,'fb122677-b907-4763-a0b8-3694f35fcab8without_registration': False} )
list_procs.update( { 'b122677-b907-4763-a0b8-3694f35fcab8f': proc_expect_comand_userfb122677b9074763a0b83694f35fcab8,'fb122677-b907-4763-a0b8-3694f35fcab8without_registration': False} )
list_procs.update( { '42a2f751-ca62-40a8-b12e-3f62ad73cb46': proc42a2f751ca6240a8b12e3f62ad73cb46,'42a2f751-ca62-40a8-b12e-3f62ad73cb46without_registration': False} )
list_procs.update( { '2a2f751-ca62-40a8-b12e-3f62ad73cb464': proc_expect_user_button_click42a2f751ca6240a8b12e3f62ad73cb46,'42a2f751-ca62-40a8-b12e-3f62ad73cb46without_registration': False} )
list_procs.update( { '54ab8048-6210-439e-a98f-79034ade1265': proc54ab80486210439ea98f79034ade1265,'54ab8048-6210-439e-a98f-79034ade1265without_registration': False} )
list_procs.update( { 'cd6e33ce-0e12-42df-bf0b-3d4b21234ccb': proccd6e33ce0e1242dfbf0b3d4b21234ccb,'cd6e33ce-0e12-42df-bf0b-3d4b21234ccbwithout_registration': False} )
list_procs.update( { 'd6e33ce-0e12-42df-bf0b-3d4b21234ccbc': proc_expect_comand_usercd6e33ce0e1242dfbf0b3d4b21234ccb,'cd6e33ce-0e12-42df-bf0b-3d4b21234ccbwithout_registration': False} )
list_procs.update( { 'e4e00055-9b82-453e-97ee-1fb091b22087': proce4e000559b82453e97ee1fb091b22087,'e4e00055-9b82-453e-97ee-1fb091b22087without_registration': False} )
list_procs.update( { '4e00055-9b82-453e-97ee-1fb091b22087e': proc_expect_user_button_clicke4e000559b82453e97ee1fb091b22087,'e4e00055-9b82-453e-97ee-1fb091b22087without_registration': False} )
list_procs.update( { 'a9fa2734-6a2c-4eeb-8a14-105ad7c7c700': proca9fa27346a2c4eeb8a14105ad7c7c700,'a9fa2734-6a2c-4eeb-8a14-105ad7c7c700without_registration': False} )
list_procs.update( { '96cb68c0-7f0a-44f1-a585-e5965c1fc8da': proc96cb68c07f0a44f1a585e5965c1fc8da,'96cb68c0-7f0a-44f1-a585-e5965c1fc8dawithout_registration': False} )
list_procs.update( { 'ba08f868-ea17-4d09-96e8-eb2b9d43be27': procba08f868ea174d0996e8eb2b9d43be27,'ba08f868-ea17-4d09-96e8-eb2b9d43be27without_registration': False} )
list_procs.update( { '6dbf09d6-a753-425e-9da0-d809dcc4049e': proc6dbf09d6a753425e9da0d809dcc4049e,'6dbf09d6-a753-425e-9da0-d809dcc4049ewithout_registration': False} )

def GetIdFirstState():
    print("stack: GetIdFirstState")
    return "e3cafc7f-e33b-41c4-b38c-40b9d62a3e55"

def GoToStateFirst(sender_id, message, state_id, data, data_user, carousel_id):
    print("stack: GoToStateFirst")
    GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)
    return

def GoToStateError(sender_id, message, state_id, data, data_user, carousel_id):
    print("stack: GoToStateError")
    GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)
    return

def GoToStateByID(sender_id, message, state_id, service_data_bot_need, data_user, carousel_id):
    print("stack: GoToStateByID")
    procedure = list_procs.get(state_id)
    if not isinstance(service_data_bot_need, dict):
        service_data_bot_need = {}
    if not isinstance(data_user, dict):
            data_user = {}
    procedure(sender_id, message, data_user, service_data_bot_need, carousel_id)

    return

def GoToCurrentState(sender_id, message, is_registered_user):
    print("stack: GoToCurrentState")
    try:
        result_restore, is_error, state_id, data, data_user, carousel_id = RestoreState(sender_id)
        if result_restore:
            print("stack: before GoToStateByID: " + state_id)
            if is_registered_user == False:
                if list_procs.get(state_id + 'without_registration') == True:
                    GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)
                else:
                    GoToStateFirst(sender_id, message, GetIdFirstState(), data, data_user, carousel_id)
            else:
                GoToStateByID(sender_id, message, state_id, data, data_user, carousel_id)
        else:
            if is_error:
                viber.send_messages(sender_id, TextMessage(text="ERROR RESTORE STATE"))
                GoToStateError(sender_id, message, GetIdErrorState(), data, data_user, carousel_id)
            else:
                GoToStateFirst(sender_id, message, GetIdFirstState(), data, data_user, carousel_id)
    except Exception as e:
        print("Ошибка при GoToCurrentState: " + e.args[0])
        viber.send_messages(sender_id, TextMessage(text="ERROR RESTORE STATE"))
        GoToStateError(sender_id, message, GetIdErrorState(), {}, {}, "")
    return

def SetHooksIfNeed():
    print("stack: SetHooksIfNeed")
    need_hook = False
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
            viber.set_webhook(request.url)

            cur.execute("INSERT INTO data_hooks (state) VALUES (%s)",
                  ("1",))
        conn.commit()
    except Exception as e:
        return False, False, e
    finally:
        cur.close()
        conn.close()
    return True, need_hook, ""

app = Flask(__name__)

viber = Api(BotConfiguration(
    name='Itilium-bot',
    avatar='http://site.com/avatar.jpg',
    auth_token=auth_token_out
))

@app.route('/',  methods=['GET'])
def IncomingGet():
    state, need_hook, error = SetHooksIfNeed()
    if state:
        if need_hook:
            return "Регистрация бота прошла успешно"
        else:
            return "Бот был зарегистрирован ранее"
    else:
        return "Ошибка при регистрации бота." + error.args[0] + "\n Попробуйте вручную (см. документацию)"

@app.route('/',  methods=['POST'])
def incoming():
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)
    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        sender_id = viber_request.sender.id
        message = viber_request.message
        is_registered_user = GetIsRegisteredUser(sender_id)
        GoToCurrentState(sender_id, message, is_registered_user)

    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.sender.id, TextMessage(text="Вы зарегистрированы"))
    elif isinstance(viber_request, ViberFailedRequest):
        viber.send_messages(viber_request.sender.id, TextMessage(text="Сообщение не отправлено"))

    return Response(status=200)
