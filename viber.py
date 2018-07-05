import os
import threading
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
import requests
import logging
from flask import Flask, request, Response
from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import json


AddressApiItilium = os.environ['AddressApiItilium']
LoginItilium = os.environ['LoginItilium']

# os.environ["PasswordItilium"] = 'ghghghghgh'
PasswordItilium = os.environ["PasswordItilium"]



logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# list_actions_senders = []

isDebug = [True]


def print_debug(value):
    if isDebug[0] == True:
        print_value(value)


def GetTextCommand(message):
    text = ""
    if (isinstance(message, str)):
        text = message
    elif (isinstance(message, TextMessage)):
        text = message.text
    else:
        text = message.text
    return text

def print_value(object_to_print, value: str = "-----------------------------"):
    print(value + "{}".format(object_to_print))


class RatingIncidents:
    need_rating: bool = False
    rating_exist: bool = True
    five_need_comment: bool = True
    four_need_comment: bool = True
    three_need_comment: bool = True
    two_need_comment: bool = False
    one_need_comment: bool = False


class StartedAction:
    def __init__(self, name: str, additional):
        self.name = name
        self.additional = additional
    def get_json(self):
        return json.dumps({"name": self.name, "additional": self.additional})

class JobItilium:

    def not_exist(self, sender, Login = "", Password = "", Adress = "" ):
        print_debug("not_exist(self, sender, Login = "", Password = "", Adress = "" )")
        if(Login == ""):
            Login = LoginItilium
        if Password == "":
            Password = PasswordItilium
        if Adress == "":
            Adress = AddressApiItilium
        try:
            quote = "\""
            response = requests.post(Adress, data = """{
                                                                  "data": {
                                                                    "action": "non_exist",
                                                                    "sender": """ + quote + sender + quote+ """, 
                                                                  }
                                                                }""",
                                                        auth=(Login,Password))
            code = response.status_code
            description = response.text

            answer = Answer()
            answer.description = description

            if(code == 200):
                answer.status = True
                answer.result = description
            else:
                answer.status = False
                answer.description = description + " ERROR CODE:" + str(code)
            return answer
        except:
            answer = Answer()
            answer.description = "Ошибка соединения с Итилиум. Обратитесь к администратору."
            answer.status = False
            return answer


    def register(self, sender, message,  Login = "", Password = "", Adress = ""):
        print_debug("def register")
        if (Login == ""):
            Login = LoginItilium
        if Password == "":
            Password = PasswordItilium
        if Adress == "":
            Adress = AddressApiItilium
        text = GetTextCommand(message)

        try:
            quote = "\""
            response = requests.post(Adress, data="""{
                                                                "data": {
                                                                "action": "register",
                                                                "sender": """ + quote + sender + quote + """,
                                                                "phone":  """ + quote + text  + quote + """,
                                                                }
                                                            }""",
                                 auth=(Login, Password))
            code = response.status_code
            description = response.text
            answer = Answer()
            if (code == 200):
                answer.status = True
                answer.result = description
            else:
                answer.status = False
                answer.description = description + " ERROR CODE:" + str(code)
            return answer
        except:
            answer = Answer()
            answer.description = "Ошибка соединения с Итилиум. Обратитесь к администратору."
            answer.status = False
            return answer


    def get_last_conversations(self, sender):
        print_debug("def get_last_conversations")
        quote = "\""
        data_to_send = """{
                                                "data": {
                                                "action": "get_last_conversations",
                                                "sender": """ + quote + sender + quote + """,                                  
                                                }
                                             }"""

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        code = response.status_code
        description = response.text
        answer = Answer()
        # print_value(description)

        # print_value(list)
        if (code == 200):
            answer.status = True
            list = json.loads(description)
            list_ret = []
            for incident in list:
                list_ret.append(WrapperView(incident.get('view'), incident.get('detail_view'), incident.get('id')))
            answer.result = list_ret
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def confirm_incident(self, sender, reference_incident, rating, comment):
        print_debug("def confirm_incident")
        quote = "\""
        data_to_send = """{
                                          "data": {
                                          "action": "confirm_incident",
                                          "sender": """ + quote + sender + quote + """,
                                          "incident": """ + quote + reference_incident + quote + """,
                                          "rating": """ + quote + str(rating) + quote + """,
                                          "comment": """ + quote + comment + quote + """,                                  
                                          }
                                       }"""
        # print_value(data_to_send)

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        # response = requests.post(AddressApiItilium, data=data_to_send,
        #                          auth=(LoginItilium, PasswordItilium))
        code = response.status_code
        description = response.text
        answer = Answer()
        if (code == 200):
            answer.status = True
            answer.result = description
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def get_rating_for_incidents_confirmation(self, sender, incident_ref):
        print_debug("def get_rating_for_incidents_confirmation")
        quote = "\""
        data_to_send = """{
                                                  "data": {
                                                  "action": "get_rating_for_incidents_confirmation",
                                                  "incident": """ + quote + incident_ref + quote + """,
                                                  "sender": """ + quote + sender + quote + """,                                  
                                                  }
                                               }"""

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        code = response.status_code
        description = response.text
        answer = Answer()
        if (code == 200):
            answer.status = True
            rating = RatingIncidents()
            dictionary = json.loads(description)
            rating.five_need_comment = dictionary.get('five_need_comment')
            rating.four_need_comment = dictionary.get('four_need_comment')
            rating.three_need_comment = dictionary.get('three_need_comment')
            rating.two_need_comment = dictionary.get('two_need_comment')
            rating.one_need_comment = dictionary.get('one_need_comment')
            rating.need_rating = dictionary.get('need_rating')
            rating.rating_exist = dictionary.get('rating_exist')
            answer.result = rating
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer


    def get_list_need_confirmed_incidents(self, sender):
        print_debug("def get_list_need_confirmed_incidents")
        quote = "\""
        data_to_send = """{
                                          "data": {
                                          "action": "list_need_confirmed_incidents",
                                          "sender": """ + quote + sender + quote + """,                                  
                                          }
                                       }"""

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        code = response.status_code
        description = response.text
        answer = Answer()
        # print_value(description)

        # print_value(list)
        if (code == 200):
            answer.status = True
            list = json.loads(description)
            list_ret = []
            for incident in list:
                list_ret.append(WrapperView(incident.get('view'), incident.get('detail_view'), incident.get('id')))
            answer.result = list_ret
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def decline_incident(self, sender, reference_incident, comment):
        print_debug("def decline_incident")
        quote = "\""
        data_to_send = """{
                                  "data": {
                                  "action": "decline_incident",
                                  "sender": """ + quote + sender + quote + """,
                                  "incident": """ + quote + reference_incident + quote + """,
                                  "comment": """ + quote + comment + quote + """,                                  
                                  }
                               }"""
        # print_value(data_to_send)

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        # response = requests.post(AddressApiItilium, data=data_to_send,
        #                          auth=(LoginItilium, PasswordItilium))
        code = response.status_code
        description = response.text
        answer = Answer()
        if (code == 200):
            answer.status = True
            answer.result = description
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def register_new_incident(self, message: str, sender: str):
        print_debug("def register_new_incident")
        quote = "\""
        message = message
        data_to_send = """{
                           "data": {
                           "action": "registration",
                           "sender": """ + quote + sender + quote + """,
                           "text":  """ + quote + message + quote + """,
                           }
                        }"""
        # print_value(data_to_send)

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'),auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        # response = requests.post(AddressApiItilium, data=data_to_send,
        #                          auth=(LoginItilium, PasswordItilium))
        code = response.status_code
        description = response.text
        answer = Answer()
        if (code == 200):
            answer.status = True
            answer.result = description
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def add_conversation(self, sender: str, reference_incident: str, text: str):
        print_debug("def add_conversation")
        quote = "\""
        data_to_send = """{
                                          "data": {
                                          "action": "add_converstaion",
                                          "sender": """ + quote + sender + quote + """,
                                          "text": """ + quote + text + quote + """,
                                          "incident": """ + quote + reference_incident + quote + """,                                  
                                          }
                                       }"""

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        code = response.status_code
        description = response.text
        answer = Answer()
        # print_value(description)

        if (code == 200):
            answer.status = True
            answer.result = description
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def get_list_open_incidents(self, sender):
        print_debug("def get_list_open_incidents")
        quote = "\""
        data_to_send = """{
                                  "data": {
                                  "action": "list_open_incidents",
                                  "sender": """ + quote + sender + quote + """,                                  
                                  }
                               }"""

        headers = {'Content-Type': 'text/xml; charset=utf-8', }
        req = requests.Request('POST', AddressApiItilium,
                               headers=headers,
                               data=data_to_send.encode('utf-8'), auth=(LoginItilium, PasswordItilium))
        prepped_requ = req.prepare()
        s = requests.Session()
        response = s.send(prepped_requ)

        code = response.status_code
        description = response.text
        answer = Answer()
        # print_value(description)

        # print_value(list)
        if (code == 200):
            answer.status = True
            list = json.loads(description)
            list_ret = []
            for incident in list:
                list_ret.append(WrapperView(incident.get('view'), incident.get('detail_view'), incident.get('id')))
            answer.result = list_ret
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer


class WrapperView:
    def __init__(self, view: str, detail_view: str, id: str):
        self.view = view
        self.id = id
        self.detail_view = detail_view


class Answer:
    status: bool = True
    result = ""
    description: str = ""


class TemplatesKeyboards:

    @staticmethod
    def get_keyboard_cancel_confirm():
        return KeyboardMessage(keyboard=
        {
            "Type": "keyboard",
            "InputFieldState": "hidden",
            "Buttons": [{
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel",
                "Text": "Отменить подтверждение"
            }]
        }
        )
    @staticmethod
    def get_keyboard_rating_with_continue():

        buttons = []
        for i in '12345':
            value = 1
            if i == '5':
                value = 2
            buttons.append({
                "Columns": value,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_Confirm_rating_" + str(i),
                "Text": str(i)
            })
        buttons.append({
            "Columns": 6,
            "Rows": 1,
            "ActionBody": "_Itilium_bot_Confirm_continue",
            "Text": "Продолжить без оценки"
        })
        buttons.append({
            "Columns": 6,
            "Rows": 1,
            "ActionBody": "_Itilium_bot_Confirm_rating_cancel",
            "Text": "Отменить"
        })
        return KeyboardMessage(keyboard={"Type": "keyboard", "Buttons": buttons})

    @staticmethod
    def get_keyboard_rating():
        buttons = []
        for i in '12345':
            value = 1
            if i == '5':
                value = 2
            buttons.append({
                "Columns": value,
                "Rows":  1,
                "ActionBody": "_Itilium_bot_Confirm_rating_" + str(i),
                "Text": str(i)
            })
        buttons.append({
            "Columns": 6,
            "Rows": 1,
            "ActionBody": "_Itilium_bot_Confirm_rating_cancel",
            "Text": "Отменить"
        })
        return KeyboardMessage(keyboard={"Type": "keyboard", "Buttons": buttons})

    @staticmethod
    def get_keyboard_on_show_conversation():
        return KeyboardMessage(keyboard=
        {
            "Type": "keyboard",
            "Buttons": [{
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_get_conversations_modify",
                "Text": "Ответить"
            }, {
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_get_conversations_close",
                "Text": "Закрыть"
            }]
        }
        )

    @staticmethod
    def get_keyboard_confirm():
        return KeyboardMessage(keyboard=
        {
            "Type": "keyboard",
            "Buttons": [{
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_Confirm",
                "Text": "Подтвердить"
            }, {
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_Decline",
                "Text": "Отклонить"
            }, {
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel_confirmation",
                "Text": "Отменить"
            }]
        }
        )

    @staticmethod
    def get_keyboard_cancel_modify():
        return KeyboardMessage(keyboard=
        {
            "Type": "keyboard",
            "Buttons": [{
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel_modify",
                "Text": "Отменить"
            }]
        }
        )

    @staticmethod
    def get_keyboard_cancel():
        return KeyboardMessage(keyboard=
        {
            "Type": "keyboard",
            "InputFieldState": "hidden",
            "Buttons": [{
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel",
                "Text": "Отменить регистрацию"
            }]
        }
        )

    @staticmethod
    def get_keyboard_start_message():
        return KeyboardMessage(keyboard=

        {
            "Type": "keyboard",
            "InputFieldState": "regular",
            # "DefaultHeight": "true",
            "Buttons": [{
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_new_incident",
                "Text": "Зарегистрировать"
            }, {
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_get_last_conversations",
                "Text": "Последние сообщения",
            },
                {
                    "Columns": 3,
                    "Rows": 1,
                    "ActionBody": "_Itilium_bot_Modify",
                    "Text": "Внести уточнения"
                }, {
                    "Columns": 3,
                    "Rows": 1,
                    "ActionBody": "_Itilium_bot_get_state",
                    "Text": "Получить статус обращений",
                }, {
                    "Columns": 6,
                    "Rows": 1,
                    "ActionBody": "_Itilium_bot_get_need_confirmed",
                    "Text": "Обращения для подтверждения",
                }]
        }
        )

    @staticmethod
    def get_keyboard_select_incident_text(list, number_parts, height_one_string = 1):
        max_buttons = 24 / height_one_string
        if (len(list) > max_buttons - 1):
            count_in_part = max_buttons - 2
            first_number = number_parts * count_in_part - count_in_part
            last_number = first_number + count_in_part - 1
            index = 0
            buttons = []
            isEnd = True
            for wrapper in list:
                if (index > last_number):
                    isEnd = False
                    break
                elif index >= first_number:
                    buttons.append({"Columns": 6, "TextHAlign": "left", "Rows": height_one_string, "ActionBody": wrapper.id, "Text": wrapper.view})
                index += 1

            if (isEnd == False):
                buttons.append({"Columns": 6, "Rows": 1, "ActionBody": "_Itilium_bot_more_incidents", "Text": "ЕЩЕ"})
            buttons.append({"Columns": 6, "Rows": 1, "ActionBody": "_Itilium_bot_cancel_modify", "Text": "Отменить"})
            text_keyboard = {"Type": "keyboard", "Buttons": buttons}
            return text_keyboard
        else:
            text_keyboard = {"Type": "keyboard"}
            buttons = []
            for wrapper in list:
                buttons.append({"Columns": 6, "TextHAlign": "left", "Rows": height_one_string, "ActionBody": wrapper.id, "Text": wrapper.view})
            buttons.append({"Columns": 6, "Rows": 1, "ActionBody": "_Itilium_bot_cancel_modify", "Text": "Отменить"})
            text_keyboard.update({"Buttons": buttons})
            return text_keyboard

    @staticmethod
    def get_keyboard_cancel_or_continue_withont_comment():
        return KeyboardMessage(keyboard={
            "Type": "keyboard",
            "Buttons": [{
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_continue",
                "Text": "Продолжить без комментария"
            }, {
                "Columns": 3,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel",
                "Text": "Отменить"
            }]
        })


class JobMessage:

    def is_start_message(self, message: str):
        print_debug("is_start_message")
        if (message.startswith("_Itilium_bot_")):
            return False
        else:
            return True

    def get_start_message_answer(self):
        print_debug("get_start_message_answer")
        return [
            TextMessage(text="Добрый день! выберите интересующее вас действие."),
            TemplatesKeyboards.get_keyboard_start_message()
        ]

    def register_incident(self, job_itilium: JobItilium, message: str, sender: str):
        print_debug("register_incident")
        answer = job_itilium.register_new_incident(message, sender)
        if answer.status:
            return [TextMessage(text="Зарегистрировано обращение:" + answer.result),
                    TemplatesKeyboards.get_keyboard_start_message()]
        else:
            return [TextMessage(text="Не удалось зарегистировать обращение по причине:" + answer.description),
                    TemplatesKeyboards.get_keyboard_start_message()]

    def start_registration(self, sender: str):
        print_debug("start_registration")
        started_action = StartedAction("Registration", "")
        SaveState(started_action,sender)
        print_debug("add started action")
        # print_debug("count:" + str(len(list_actions_senders)))
        return [TextMessage(text="Опишите вашу проблему."), TemplatesKeyboards.get_keyboard_cancel()]

    def start_itilium_modification(self, sender: str):
        print_debug("start_itilium_modification")
        job_itilium = JobItilium()
        answer = job_itilium.get_list_open_incidents(sender)
        if answer.status:
            list = answer.result
            if len(list) == 0:
                return [TextMessage(text="У вас нет зарегистрированных открытых обращений"),
                        TemplatesKeyboards.get_keyboard_start_message()]
            elif len(list) == 1:
                started_action = StartedAction("AddConversationsInputText", list[0].id)
                SaveState(started_action, sender)
                return [TextMessage(text="Введите уточнение:"), TextMessage(text=list[0].detail_view),
                        TemplatesKeyboards.get_keyboard_cancel_modify()]
            else:
                started_action = StartedAction("AddConversationsSelectIncident", {"number": 1, "list": list})
                SaveState(started_action, sender)
                list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                    keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                                  started_action.additional.get("number"),2))]
                return list_answer
        else:
            return [TextMessage(text="Ошибка." + answer.description),
                    TemplatesKeyboards.get_keyboard_start_message()]


    def start_get_state(self, sender: str):
        print_debug("start_get_state")
        job_itilium = JobItilium()
        list = job_itilium.get_list_open_incidents(sender)
        if len(list) == 0:
            return [TextMessage(text="У вас нет зарегистрированных открытых обращений"),
                    TemplatesKeyboards.get_keyboard_start_message()]
        elif len(list) == 1:
            return [TextMessage(text="Детальная информация:"), TextMessage(text=list[0].detail_view),
                    TemplatesKeyboards.get_keyboard_start_message()]
        else:
            started_action = StartedAction("GetStateSelectIncident", {"number": 1, "list": list})
            SaveState(started_action,sender)
            list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"),2))]
            return list_answer

    def start_get_need_confirmed(self, sender: str):
        print_debug("start_get_need_confirmed")
        job_itilium = JobItilium()
        list = job_itilium.get_list_need_confirmed_incidents(sender)
        if len(list) == 0:
            return [TextMessage(text="Нет обращений, требующих подтверждения"),
                    TemplatesKeyboards.get_keyboard_start_message()]
        elif len(list) == 1:
            return [TextMessage(text="Детальная информация:"), TextMessage(text=list[0].detail_view),
                    TemplatesKeyboards.get_keyboard_confirm()]
        else:
            started_action = StartedAction( "GetConfirmedSelectIncident", {"number": 1, "list": list})
            SaveState(started_action,sender)
            list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"),2))]
            return list_answer

    def start_get_last_conversations(self, sender):
        print_debug("start_get_last_conversations")
        job_itilium = JobItilium()
        list = job_itilium.get_last_conversations(sender)

        if len(list) == 0:
            return [TextMessage(text="Нет сообщений за последние 5 дней"), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            started_action = StartedAction("GetLastConversations", {"number": 1, "list": list})
            SaveState(started_action, sender)
            list_answer = [TextMessage(text="Выберите сообщение для уточнения или просмотра"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"), 2))]
            return list_answer



    def on_command_select(self, message: str, sender: str):
        print_debug("on_command_select")
        if (message == "_Itilium_bot_new_incident"):
            return self.start_registration(sender)
        elif (message == "_Itilium_bot_Modify"):
            return self.start_itilium_modification(sender)
        elif (message == "_Itilium_bot_get_state"):
            return self.start_get_state(sender)
        elif (message == "_Itilium_bot_get_need_confirmed"):
            return self.start_get_need_confirmed(sender)
        elif (message == "_Itilium_bot_get_last_conversations"):
            return self.start_get_last_conversations(sender)
        else:
            return TextMessage(text="Не реализовано, обратитесь к разработчику")

    def get_started_action(self, sender: str):
        value = GetState(sender)
        if value == "":
            return None
        else:
            return StartedAction(value["Name"], value["additional"])

    def sender_has_started_actions(self, sender: str):
        return self.get_started_action(sender) != None

    def remove_started_action(self, sender: str):
        print_debug("remove_started_action")
        SaveState("", sender)

    def continue_registration(self, message, sender: str):
        print_debug("continue_registration")
        job_itilium = JobItilium()
        self.remove_started_action(sender)
        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel"):
            return [TextMessage(text="Регистрация отменена"), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            return self.register_incident(job_itilium, command, sender)

    def continue_confirmed_input_comment(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_confirmed_input_comment")
        command = self.get_text_comand(message)
        reference_incident = started_action.additional.get("ref")
        rating = started_action.additional.get("rating")
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_cancel"):
            return [TextMessage(text="Подтверждение не выполнено"), TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_continue":  # Пользователю эта кнопка недоступна может быть, но он может ввести эту команду. На самом деле, если пользователь не хочет комментировать, то и не надо его заставлять
            job_itilium = JobItilium()
            answer = job_itilium.confirm_incident(sender, reference_incident, rating, "")
            if (answer == False):
                return [TextMessage(text="Не удалось подтвердить обращение по причине:" + answer.description)]
            else:
                return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]
        else:  # Комментарий введен
            job_itilium = JobItilium()
            answer = job_itilium.confirm_incident(sender, reference_incident, rating, command)
            if (answer == False):
                return [TextMessage(text="Не удалось подтвердить обращение по причине:" + answer.description)]
            else:
                return [TextMessage(text=answer.description),TemplatesKeyboards.get_keyboard_start_message()]

    def continue_confirmed_select_rating(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_confirmed_select_rating")
        command = self.get_text_comand(message)
        reference_incident = started_action.additional.get("ref")
        rating_state: RatingIncidents = started_action.additional.get("rating_state")
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_Confirm_rating_cancel"):
            return [TextMessage(text="Подтверждение не выполнено:"), TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_Confirm_continue":

            job_itilium = JobItilium()
            answer = job_itilium.confirm_incident(sender, reference_incident, -1,"")
            if (answer == False):
                return [TextMessage(text="Не удалось подтвердить обращение по причине:" + answer.description)]
            else:
                return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            need_comment = False
            rating = -1
            if command == "_Itilium_bot_Confirm_rating_1":
                rating = 1
                if rating_state.one_need_comment == True:
                    need_comment = True
            elif command == "_Itilium_bot_Confirm_rating_2":
                rating = 2
                if rating_state.two_need_comment == True:
                    need_comment = True
            elif command == "_Itilium_bot_Confirm_rating_3":
                rating = 3
                if rating_state.three_need_comment == True:
                    need_comment = True
            elif command == "_Itilium_bot_Confirm_rating_4":
                rating = 4
                if rating_state.four_need_comment == True:
                    need_comment = True
            elif command == "_Itilium_bot_Confirm_rating_5":
                rating = 5
                if rating_state.five_need_comment == True:
                    need_comment = True

            started_action = StartedAction( "Get_Comfirmed_input_comment",
                                           {"ref": reference_incident, "rating": rating})
            SaveState(started_action, sender)
            if need_comment:
                return [TextMessage(text="Данная оценка требует комментарий:"),
                        TemplatesKeyboards.get_keyboard_cancel_confirm()]
            else:
                return [TextMessage(text="Укажите комментарий к оценке"),
                        TemplatesKeyboards.get_keyboard_cancel_or_continue_withont_comment()]

    def continue_confirmed_select_buttons(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_confirmed_select_buttons")
        command = self.get_text_comand(message)
        reference_incident = started_action.additional
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_Confirm"):
            job_itilium = JobItilium()
            answer = job_itilium.get_rating_for_incidents_confirmation(sender, reference_incident)
            if answer.status:
                rating_state = answer.result
                # print_value(rating_state.need_rating)
                if rating_state.need_rating:
                    started_action = StartedAction( "Get_Comfirmed_select_rating",
                                                   {"ref": reference_incident, "rating_state": rating_state})
                    SaveState(started_action, sender)
                    return [ TextMessage(text="Оцените выполнение обращения"), TemplatesKeyboards.get_keyboard_rating()]
                elif rating_state.rating_exist:
                    started_action = StartedAction( "Get_Comfirmed_select_rating",
                                                   {"ref": reference_incident, "rating_state": rating_state})
                    SaveState(started_action, sender)
                    return [TextMessage(text="Оцените выполнение обращения"), TemplatesKeyboards.get_keyboard_rating_with_continue()]
                else:
                    job_itilium = JobItilium()
                    answer = job_itilium.confirm_incident(sender, reference_incident, -1, "")
                    if (answer == False):
                        return [TextMessage(text="Не удалось подтвердить обращение по причине:" + answer.description)]
                    else:
                        return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]
            else:
                return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_Decline":

            started_action = StartedAction( "Get_decline_input_comment",
                                           {"ref": reference_incident})
            SaveState(started_action, sender)
            return [TextMessage(text="Укажите причину отклонения"),
                    TemplatesKeyboards.get_keyboard_cancel()]


        else:  # cancel
            return [TextMessage(text="Подтверждение не выполнено:"), TemplatesKeyboards.get_keyboard_start_message()]

    def continue_get_last_conversations_select_actions(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_get_last_conversations_select_actions")
        reference = started_action.additional
        self.remove_started_action(sender)
        command = self.get_text_comand(message)
        if command == "_Itilium_bot_get_conversations_modify":
            started_action = StartedAction( "AddConversationsInputText", reference)
            SaveState(started_action, sender)
            return [TextMessage(text="Введите уточнение"),
                    TemplatesKeyboards.get_keyboard_cancel_modify()]

        elif command == "_Itilium_bot_get_conversations_close":
            return [TemplatesKeyboards.get_keyboard_start_message()]



    def continue_get_last_conversations(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_get_last_conversations")
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)

        if (command == "_Itilium_bot_cancel_modify"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction( "GetLastConversations",
                                           {"number": number_page + 1, "list": list})
            SaveState(started_action,sender)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1, 2))]

            return list_answer
        else:
            started_action = StartedAction("GetLastConversation_select_action", command)
            SaveState(started_action,sender)
            detail_view = ""
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    break
            return [TextMessage(text="Детальная информация:"), TextMessage(text=detail_view),
                    TemplatesKeyboards.get_keyboard_on_show_conversation()]



    def continue_get_confirmed_select_incident(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_get_confirmed_select_incident")
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel_confirmation"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction( "GetConfirmedSelectIncident",
                                           {"number": number_page + 1, "list": list})
            SaveState(started_action, sender)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1,2))]

            return list_answer
        else:
            started_action = StartedAction( "GetConfirmed_SelectButtonsConfirmDecline", command)
            SaveState(started_action,sender)
            detail_view = ""
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    break
            return [TextMessage(text="Подтвердите или отклоните выполнение обращения:"), TextMessage(text=detail_view),
                    TemplatesKeyboards.get_keyboard_confirm()]

    def continue_get_state_select_incident(self, message, sender, started_action: StartedAction):
        print_debug("continue_get_state_select_incident")
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel_modify"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction( "GetStateSelectIncident",
                                           {"number": number_page + 1, "list": list})
            SaveState(started_action,sender)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1,2))]

            return list_answer
        else:
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    break
            return [TextMessage(text=detail_view), TemplatesKeyboards.get_keyboard_start_message()]

    def continue_add_conversations_select_incident(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_add_conversations_select_incident")
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        command = self.get_text_comand(message)

        if (command == "_Itilium_bot_cancel_modify"):
            self.remove_started_action(sender)
            return [TextMessage(text="Уточнения не внесены"), TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            self.remove_started_action(sender)
            started_action = StartedAction("AddConversationsSelectIncident",
                                           {"number": number_page + 1, "list": list})
            SaveState(started_action,sender)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1,2))]

            return list_answer
        else:
            self.remove_started_action(sender)
            started_action = StartedAction("AddConversationsInputText", command)

            detail_view = ""
            found = 0
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    found = 1
                    break
            if (found == 1):
                SaveState(started_action,sender)
                return [TextMessage(text="Введите уточнение:"), TextMessage(text=detail_view),
                        TemplatesKeyboards.get_keyboard_cancel_modify()]
            return self.get_start_message_answer()  # Не то ввел пользователь. Сначала

    def continue_add_conversations_input_text(self, message, sender: str, started_action: StartedAction):
        print_debug("continue_add_conversations_input_text")
        command = self.get_text_comand(message)
        reference = started_action.additional
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_cancel_modify"):
            return [TextMessage(text="Уточнения не внесены"), TemplatesKeyboards.get_keyboard_start_message()]
        job_itilium = JobItilium()
        answer = job_itilium.add_conversation(sender, reference, command)
        if (answer.status == False):
            return [TextMessage(text="Не удалось внести уточнения по причине:{}".format(answer.description)),
                    TemplatesKeyboards.get_keyboard_start_message()]
        else:
            return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]

    def continue_decline_incident_input_text(self, message, sender, started_action):
        print_debug("continue_decline_incident_input_text")
        command = self.get_text_comand(message)
        reference = started_action.additional.get("ref")
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_cancel"):
            return [TextMessage(text="Обращение не отклонено"), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            job_itilium = JobItilium()
            answer = job_itilium.decline_incident(sender, reference, command)
            if (answer == False):
                return [TextMessage(text="Не удалось отклонить обращение по причине:" + answer.description),
                        TemplatesKeyboards.get_keyboard_start_message()]
            else:
                return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]

    def continue_started_process(self, message, sender: str):
        print_debug("continue started process")
        started_action = self.get_started_action(sender)
        if (started_action.name == "Registration"):
            return self.continue_registration(message, sender)
        elif started_action.name == "GetConfirmed_SelectButtonsConfirmDecline":
            return self.continue_confirmed_select_buttons(message, sender, started_action)
        elif started_action.name == "Get_Comfirmed_input_comment":
            return self.continue_confirmed_input_comment(message, sender, started_action)
        elif started_action.name == "Get_Comfirmed_select_rating":
            return self.continue_confirmed_select_rating(message, sender, started_action)
        elif started_action.name == "GetConfirmedSelectIncident":
            return self.continue_get_confirmed_select_incident(message, sender, started_action)
        elif started_action.name == "GetLastConversations":
            return self.continue_get_last_conversations(message, sender, started_action)
        elif started_action.name == "GetLastConversation_select_action":
            return self.continue_get_last_conversations_select_actions(message, sender, started_action)
        elif started_action.name == "GetStateSelectIncident":
            return self.continue_get_state_select_incident(message, sender, started_action)
        elif started_action.name == "AddConversationsSelectIncident":
            return self.continue_add_conversations_select_incident(message, sender, started_action)
        elif started_action.name == "AddConversationsInputText":
            return self.continue_add_conversations_input_text(message, sender, started_action)
        elif started_action.name == "Get_decline_input_comment":
            return self.continue_decline_incident_input_text(message, sender, started_action)

        else:
            return [TextMessage(text="Не реализовано "), TemplatesKeyboards.get_keyboard_start_message()]

    def get_text_comand(self, message):
        print_debug("get_text_comand")
        return GetTextCommand(message)

    def first_level_comand(self, message, sender: str):
        print_debug("first level comand")
        text = self.get_text_comand(message)
        if (self.is_start_message(text)):
            return self.get_start_message_answer()
        else:
            return self.on_command_select(text, sender)

    def process(self, message, sender: str):
        print_debug("process")
        if (self.sender_has_started_actions(sender) == False):
            print_debug("NO started action")
            return self.first_level_comand(message, sender)
        else:
            print_debug("has started action")
            return self.continue_started_process(message, sender)


class Integration:
    def on_new_message(self, message, sender: str):
        print_debug("on_new_message")
        job = JobMessage()
        retMessage = job.process(message, sender)
        return retMessage

    def on_subscribe(self, sender: str):
        return TextMessage(text="Спасибо, что подписались!")

    def on_failed_message(self, message: str, sender: str):
        logger.warning("client failed receiving message. failure: {0}".format(message))


auth_token_out = '4807270b7ee7d14d-fa37d43de286a0ef-be81bbab61de274b'
app = Flask(__name__)

viber = Api(BotConfiguration(
    name='Itilium-bot',
    avatar='http://site.com/avatar.jpg',
    auth_token=auth_token_out
))


def SaveValueToEnviron(value, NameEnviron, sender):
    lock = threading.Lock()
    lock.acquire()
    try:
        data = os.environ[NameEnviron]
        if data == "":
            os.environ[NameEnviron] = json.dumps([{"sender":sender,"state":value}])
            return
        else:
            data = json.loads(data)
            for senderid in data:
                if senderid.get("sender") == sender:
                    senderid["state"] = value
                    os.environ[NameEnviron] = json.dumps(data)
                    return
            data.append({"sender":sender,"state": value})
            os.environ[NameEnviron] = json.dumps(data)
    finally:
        lock.release()

def LoadValueFromEnviron(NameEnviron, sender):
    data = os.environ[NameEnviron]
    if data == "":
        return ""
    list = json.loads(data)
    for senderid in list:
        if senderid.get("sender") == sender:
            data_ret = senderid.get("state")
            if data_ret == "":
                return data_ret
            else:
                return json.loads(data_ret)
    return ""

def SaveState(started_action, sender):
    if isinstance(started_action,StartedAction):
        SaveValueToEnviron(started_action.get_json(), "temp_data_fields", sender)
    else:
        SaveValueToEnviron(json.dumps({"value":started_action}), "temp_data_fields", sender)

def GetState(sender):
    value = LoadValueFromEnviron("temp_data_fields", sender)
    return value

def GetIsRegistration(sender):
    value = LoadValueFromEnviron("registration_fields", sender)
    if value == "":
        return False
    else:
        if value.get("value"):
            return True
        else:
            return False

def SetIsRegistration(sender, state:bool ):
    SaveValueToEnviron(json.dumps({"value":state}), "registration_fields", sender)

def VerifyRegistration(senderid, message ):
    # print_debug("test begin registration")
    # job_itilium = JobItilium()
    # if GetIsRegistration("555") == False:
    #     SetIsRegistration("555", True)
    #     if GetIsRegistration("555") == True:
    #         print_debug("OK")
    #     else:
    #         print_debug("Error")
    # print_debug("test end registration")

    print_debug("Verify registration")
    job_itilium = JobItilium()
    if GetIsRegistration(senderid) == False:
        print_debug("-Verify registration false")
        answer = job_itilium.not_exist(senderid)
        if answer.status:
            if (answer.result == str(1)):
                print_debug("-Verify registration non exist")
                ret = TextMessage(text="Укажите свой номер телефона в формате +7хххххххххх")
                SetIsRegistration( senderid, True)
                print_value("is registrations {}".format(GetIsRegistration(senderid)))
                return True, ret
            else:
                print_debug("-Verify registration exist")
                return False, None
        else:
            ret = TextMessage(text=answer.description)
            return True, ret
    elif GetIsRegistration(senderid) == True:
        print_debug("-Verify registration true")
        answer = job_itilium.register(senderid, message)
        if answer.status == True:
            if (answer.result == str(1)):
                print_debug("-Verify registration register")
                SetIsRegistration(senderid, False)
                return False, None
            else:
                ret = [TextMessage(text=answer.result),
                       TextMessage(text="Укажите свой номер телефона в формате +7хххххххххх")]
                return True, ret

        else:
            ret = TextMessage(text=answer.description)
            return True, ret
    else:
        return False, None


@app.route('/',  methods=['POST'])
def incoming():
    print_debug("incoming message")

    # print_debug("count started actions:" + str(len(list_actions_senders)))
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method

    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    integration = Integration()

    if isinstance(viber_request, ViberMessageRequest):

        print_debug("incoming message:" + viber_request.message.text)

        job = JobItilium()
        print_debug("sender_has_started_actions(sender) {}".format(job.sender_has_started_actions(viber_request.sender.id)))

        isReg, mess = VerifyRegistration(viber_request.sender.id, viber_request.message)
        if isReg:
            viber.send_messages(viber_request.sender.id, mess)
        else:
            viber.send_messages(viber_request.sender.id, integration.on_new_message(viber_request.message, viber_request.sender.id))

    elif isinstance(viber_request, ViberSubscribedRequest):
        print_debug("subscribe message")
        viber.send_messages(viber_request.sender.id, integration.on_subscribe(viber_request.sender.id))
    elif isinstance(viber_request, ViberFailedRequest):
        print_debug("failed request")
        integration.on_failed_message(viber_request.message, viber_request.sender.id)
    else:
        print_debug("others")

    return Response(status=200)

# integration = Integration()
# senderid = "RH2xtdiCKsztWpOkGlMxZQ=="
########################################################################################################################
##          TESTS                                                            ###########################################
########################################################################################################################

_AddressApiItilium = AddressApiItilium
_LoginItilium = LoginItilium
_PasswordItilium = PasswordItilium

def test_non_exist():
    job_itilium = JobItilium()

    print_value("test non exist begin")

    answer = job_itilium.not_exist("sddsdddddd", _LoginItilium, _PasswordItilium, _AddressApiItilium )
    if answer.status == True and answer.result == str(1):
        print_value("ok")
    else:
        print_value("false non exist 1")

    answer = job_itilium.not_exist("222", _LoginItilium, _PasswordItilium, _AddressApiItilium) #для теста завести в Итиилиум в регистр ИдентификаторыВМессенджерах запись, где идентификатор = 222
    if answer.status == True and answer.result == str(0):
        print_value("ok")
    else:
        print_value("false non exist 2")

    answer = job_itilium.not_exist("293", _LoginItilium + "ddd", _PasswordItilium, _AddressApiItilium)
    if answer.status == False:
        print_value("ok")
    else:
        print_value("false non exist 3")

    answer = job_itilium.not_exist("293", _LoginItilium, _PasswordItilium + "f", _AddressApiItilium)
    if answer.status == False:
        print_value("ok")
    else:
        print_value("false non exist 4")

    answer = job_itilium.not_exist("293", _LoginItilium, _PasswordItilium , _AddressApiItilium + "ff")
    if answer.status == False:
        print_value("ok")
    else:
        print_value("false non exist 4")

    print_value("test non exist end")

def test_register():

    job_itilium = JobItilium()

    print_value("test registr begin")

    answer = job_itilium.register("222","-----",_LoginItilium,_PasswordItilium,_AddressApiItilium)
    if answer.status == True and answer.result != str(1):
        print_value("ok")
    else:
        print_value("false in register 1")

    answer = job_itilium.register("222", "293", _LoginItilium, _PasswordItilium, _AddressApiItilium) #надо вподключенном итилиум добавить в регистр контактная информация физлицо с телефоном 293
    if answer.status == True and answer.result == str(1):
        print_value("ok")
    else:
        print_value("false in register 2")

    answer = job_itilium.register("222", "293", _LoginItilium + "s", _PasswordItilium,
                                  _AddressApiItilium)  # надо вподключенном итилиум добавить в регистр контактная информация физлицо с телефоном 293
    if answer.status == False :
        print_value("ok")
    else:
        print_value("false in register 3")

    answer = job_itilium.register("222", "293", _LoginItilium , _PasswordItilium + "d",
                                  _AddressApiItilium)  # надо вподключенном итилиум добавить в регистр контактная информация физлицо с телефоном 293
    if answer.status == False:
        print_value("ok")
    else:
        print_value("false in register 4")

    answer = job_itilium.register("222", "293", _LoginItilium, _PasswordItilium,
                                  _AddressApiItilium + "d")  # надо вподключенном итилиум добавить в регистр контактная информация физлицо с телефоном 293
    if answer.status == False:
        print_value("ok")
    else:
        print_value("false in register 5")
    print_value("test registr end")

def test_VerifyRegistration():
    print_value("VerifyRegistration begin") #НАДО УДАЛИТЬ В ИТИЛИУМ ИЗ РЕГИСТРА ИдентификаторыПодписчиков запись, с ИДентификатором 111
    isReg, mess = VerifyRegistration("111","Hello")
    if isReg :
        print_value("ok")
    else:
        print_value("false VerifyRegistration 1")
        return
    isReg, mess = VerifyRegistration("111", "-----")
    if isReg :
        print_value("ok")
        isReg, mess = VerifyRegistration("111", "293") # надо вподключенном итилиум добавить в регистр контактная информация физлицо с телефоном 293
        if(isReg == False):
            print_value("ok")
        else:
            print_value("false VerifyRegistration 3")
    else:
        print_value("false VerifyRegistration 2")
        return

    print_value("VerifyRegistration end")

def test_Registration():
    print_value("Registration begin")
    integration = Integration()
    value = integration.on_new_message("hello", "111") #пользователь 111 должен быть в регистре ИдентификаторыПодписчиков. В тестах выше по сценарию он добавлен
    job_message = JobMessage()
    try:
        if isinstance(value[0],TextMessage) and isinstance(value[1], KeyboardMessage):
            print_value("ok")
            if value[1].keyboard == TemplatesKeyboards.get_keyboard_start_message().keyboard:
                print_value("ok")
            else:
                print_value("false 2")
        else:
            print_value("false 1")
    except:
        print_value("false 1")
    print_value("Registration end")

def test_registerNewIncident():
    print_value("registerNewIncident begin")
    job_itilium = JobItilium()
    answer = job_itilium.register_new_incident("новое Обращение","RH2xtdiCKsztWpOkGlMxZQ")
    if answer.status:
        print_value("ok " + answer.result)
    else:
        print_value("false 1" + answer.description)
    print_value("registerNewIncident end")

def test_GetListOpenIncidents():
    print_value("GetListOpenIncidents end")
    job_itilium = JobItilium()
    answer = job_itilium.get_list_open_incidents( "111")
    if answer.status:
        print_value("ok " )
    else:
        print_value("false 1")
    print_value("GetListOpenIncidents end")

def test_AddConversation():
    print_value("AddConversation begin")
    job_itilium = JobItilium()
    answer = job_itilium.get_list_open_incidents("111")
    if answer.status:
        if len(answer.result) == 0:
            print_value("false no incidents in base")
        else:
            incident_id = answer.result[0].id
            answer = job_itilium.add_conversation("111",incident_id, "новое сообщение через add conversation")
            if answer.status:
                print_value("ok " + answer.result)
            else:
                print_value("false 1 " + answer.description)
    else:
        print_value("false see test get_list_open_incidents")


    print_value("AddConversation end")

def  test_DeclineIncident():
    print_value("DeclineIncident begin")

    job_itilium = JobItilium()
    answer = job_itilium.get_list_need_confirmed_incidents("111")
    if answer.status:
        if len(answer.result) == 0:
            print_value("false no incidents in base")
        else:
            incident_id = answer.result[0].id
            answer = job_itilium.decline_incident("111", incident_id, "не нравится, как сделано, переделайте")
            if answer.status:
                print_value("ok " + answer.result)
            else:
                print_value("false 1 " + answer.description)
    else:
        print_value("false see test get_list_open_incidents")

    print_value("DeclineIncident end")

def test_GetNeedConfirmed():
    print_value("test_GetNeedConfirmed begin")
    job_itilium = JobItilium()
    answer = job_itilium.get_list_need_confirmed_incidents("111")
    if answer.status:
        print_value("ok ")
    else:
        print_value("false 1" + answer.description)
    print_value("test_GetNeedConfirmed end")


def test_getRatingConfirmation():
    print_value("test_getRatingConfirmation begin")
    job_itilium = JobItilium()
    answer = job_itilium.get_list_need_confirmed_incidents("111")
    if answer.status:
        if len(answer.result) == 0:
            print_value("false no incidents in base")
        else:
            incident_id = answer.result[0].id
            answer = job_itilium.get_rating_for_incidents_confirmation("111", incident_id)
            if answer.status:
                print_value("ok " + answer.result)
            else:
                print_value("false 1 " + answer.description)

    else:
        print_value("false 1" + answer.description)
    print_value("test_getRatingConfirmation end")

def test_ConfirmIncident():
    print_value("test_ConfirmIncident begin")
    job_itilium = JobItilium()
    answer = job_itilium.get_list_need_confirmed_incidents("111")
    if answer.status:
        if len(answer.result) == 0:
            print_value("false no incidents in base")
        else:
            incident_id = answer.result[0].id
            answer = job_itilium.confirm_incident("111", incident_id, 3, "Слабенько")
            if answer.status:
                print_value("ok " + answer.result)
            else:
                print_value("false 1 " + answer.description)
    else:
        print_value("false see test get_list_open_incidents")

    print_value("test_ConfirmIncident end")

def test_getLastConversations():
    print_value("test_ConfirmIncident begin")
    job_itilium = JobItilium()
    answer = job_itilium.get_last_conversations("111")
    if answer.status:
        print_value("ok")
        for i in answer.result:
            print_value(i.view)
            print_value(i.detail_view)
            print_value(i.id)
    else:
        print_value("false " + answer.description)
    print_value("test_ConfirmIncident end")

def test_GetSetRegistrations():
    state_reg = GetIsRegistration("111")
    if state_reg == False:
        print_value("ok")
        SetIsRegistration("111", True)
        state_reg = GetIsRegistration("111")
        if state_reg == True:
            print_value("ok")
            state_reg = GetIsRegistration("222")
            if state_reg == False:
                print_value("ok")
                SetIsRegistration("111", False)
                state_reg = GetIsRegistration("222")
                if state_reg == False:
                    print_value("ok")
                    SetIsRegistration("222", True)
                    state_reg = GetIsRegistration("222")
                    if state_reg == True:
                        print_value("ok")
                        state_reg = GetIsRegistration("111")
                        if state_reg == False:
                            print_value("ok")
                        else:
                            print_value("false 6")
                    else:
                        print_value("false 5")
                else:
                    print_value("false 4")
            else:
                print_value("false 3")
        else:
            print_value("false 2")
    else:
        print_value("false 1")

def test_load_save_environ():
    state_reg = LoadValueFromEnviron("state_users","111")
    if state_reg == "":
        print_value("ok")
        SaveValueToEnviron(StartedAction("test action", {"param": "1", "reference": "dddddfdfdfdfdfdf"}).get_json(),
                           "state_users", "111")
        state_reg = LoadValueFromEnviron("state_users", "111")
        if state_reg["name"] == "test action" and state_reg["additional"]["param"] == "1":
            print_value("ok")
            state_reg = LoadValueFromEnviron("state_users", "222")
            if state_reg == "":
                print_value("ok")
                SaveValueToEnviron("", "state_users", "111")
                state_reg = LoadValueFromEnviron("state_users","222")
                if state_reg == "":
                    print_value("ok")
                    SaveValueToEnviron(StartedAction("test action 2", {"param": "2", "reference": "dddddfdfdfdfdfdf"}).get_json(),
                                       "state_users", "222")
                    state_reg = LoadValueFromEnviron("state_users", "222")
                    if state_reg["name"] == "test action 2" and state_reg["additional"]["param"] == "2":
                        print_value("ok")
                        state_reg = LoadValueFromEnviron("state_users", "111")
                        if state_reg == "":
                            print_value("ok")
                        else:
                            print_value("false 6")
                    else:
                        print_value("false 5")
                else:
                    print_value("false 4")
            else:
                print_value("false 3")
        else:
            print_value("false 2")
    else:
        print_value("false 1")

def tests():
    # test_non_exist()
    # test_register()
    # test_VerifyRegistration()
    # test_Registration()
    # test_registerNewIncident()
    # test_GetListOpenIncidents()
    # test_AddConversation()
    # test_GetNeedConfirmed()
    # test_DeclineIncident()
    # test_getRatingConfirmation()
    # test_ConfirmIncident()
    # test_getLastConversations()
    # test_GetSetRegistrations()
    # test_load_save_environ()
    pass
tests()

if __name__ == '__main__':
     port = int(os.environ.get('PORT', 5000))
     app.run(host='0.0.0.0', port=port, debug=True)