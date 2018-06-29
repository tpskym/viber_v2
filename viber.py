
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



AddressApiItilium = "http://demo.desnol.ru/suhov_itil/hs/viberapi/action"
LoginItilium = "admin"
PasswordItilium = "1Q2w3e4r5t"

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

list_actions_senders = []


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
    def __init__(self, sender: str, name: str, additional):
        self.sender = sender
        self.name = name
        self.additional = additional


class JobItilium:

    def not_exist(self, sender, Login = "", Password = "", Adress = "" ):
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
        print(sender)
        list = []
        for i in range(50):
            list.append(WrapperView(
                "00000000" + str(i) + " от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить<br> <B>Иванов Петр васильевич:</B><br>  Что именно не работает?<br><b>Cидоров Иван:</b> Все не работает ?",
                "Иванов Петр васильевич: \r Детальное описание с ссобщениями,от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 "
                "Сидоров Иван Николаевич:\r Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить",
                "referenceInItilium" + str(i)))
        return list

    def confirm_incident(self, sender, reference_incident, rating, comment):
        answer = Answer()
        answer.description = "Обращение подтверждено"
        return answer

    def get_rating_for_incidents_confirmation(self, sender, incident_ref):
        return RatingIncidents

    def get_list_need_confirmed_incidents(self, sender):
        list = []
        for i in range(50):
            list.append(WrapperView(
                "00000000" + str(i) + " от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить",
                "Иванов Петр васильевич: \r Детальное описание с ссобщениями,от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 \r\r"
                "Сидоров Иван Николаевич: \r Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить",
                "referenceInItilium" + str(i)))
        return list

    def decline_incident(self, sender, command):
        answer = Answer()
        answer.description = "Результат обращения отклонен"
        return answer

    def register_new_incident(self, message: str, sender: str):
        quote = "\""
        response = requests.post(AddressApiItilium, data="""{
                                                                       "data": {
                                                                       "action": "registrations",
                                                                       "sender": """ + quote + sender + quote + """,
                                                                       "phone":  """ + quote + message + quote + """,
                                                                       }
                                                                   }""",
                                 auth=(LoginItilium, PasswordItilium))
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
        answer = Answer()
        answer.description = "Уточнения внесены"
        return answer

    def get_list_open_incidents(self, sender):
        list = []
        for i in range(2):
            list.append(WrapperView(
                "00000000" + str(i) + " от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить",
                "Детальное описание с ссобщениями,от 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починитьот 12/06/2018 Не работает принтер уже вторую неделю, надо срочно починить",
                "referenceInItilium" + str(i)))
        return list

        # return ["000000002 от 12/06/2018","000000001 от 12/06/2018", "000000003 от 12/06/2018"]


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
        if (message.startswith("_Itilium_bot_")):
            return False
        else:
            return True

    def get_start_message_answer(self):
        return [
            TextMessage(text="Добрый день! выберите интересующее вас действие."),
            TemplatesKeyboards.get_keyboard_start_message()
        ]

    def register_incident(self, job_itilium: JobItilium, message: str, sender: str):
        answer = job_itilium.register_new_incident(message, sender)
        if (answer.status):
            return [TextMessage(text="Зарегистрировано обращение:" + answer.description),
                    TemplatesKeyboards.get_keyboard_start_message()]
        else:
            return [TextMessage(text="Не удалось зарегистировать обращение по причине:" + answer.description),
                    TemplatesKeyboards.get_keyboard_start_message()]

    def start_registration(self, sender: str):
        started_action = StartedAction(sender, "Registration", "")
        list_actions_senders.append(started_action)
        return [TextMessage(text="Опишите вашу проблему."), TemplatesKeyboards.get_keyboard_cancel()]

    def start_itilium_modification(self, sender: str):
        job_itilium = JobItilium()
        list = job_itilium.get_list_open_incidents(sender)
        if len(list) == 0:
            return [TextMessage(text="У вас нет зарегистрированных открытых обращений"),
                    TemplatesKeyboards.get_keyboard_start_message()]
        elif len(list) == 1:
            started_action = StartedAction(sender, "AddConversationsInputText", list[0].id)
            list_actions_senders.append(started_action)
            return [TextMessage(text="Введите уточнение:"), TextMessage(text=list[0].detail_view),
                    TemplatesKeyboards.get_keyboard_cancel_modify()]
        else:
            started_action = StartedAction(sender, "AddConversationsSelectIncident", {"number": 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"),2))]
            return list_answer

    def start_get_state(self, sender: str):
        job_itilium = JobItilium()
        list = job_itilium.get_list_open_incidents(sender)
        if len(list) == 0:
            return [TextMessage(text="У вас нет зарегистрированных открытых обращений"),
                    TemplatesKeyboards.get_keyboard_start_message()]
        elif len(list) == 1:
            return [TextMessage(text="Детальная информация:"), TextMessage(text=list[0].detail_view),
                    TemplatesKeyboards.get_keyboard_start_message()]
        else:
            started_action = StartedAction(sender, "GetStateSelectIncident", {"number": 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"),2))]
            return list_answer

    def start_get_need_confirmed(self, sender: str):
        job_itilium = JobItilium()
        list = job_itilium.get_list_need_confirmed_incidents(sender)
        if len(list) == 0:
            return [TextMessage(text="Нет обращений, требующих подтверждения"),
                    TemplatesKeyboards.get_keyboard_start_message()]
        elif len(list) == 1:
            return [TextMessage(text="Детальная информация:"), TextMessage(text=list[0].detail_view),
                    TemplatesKeyboards.get_keyboard_confirm()]
        else:
            started_action = StartedAction(sender, "GetConfirmedSelectIncident", {"number": 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [TextMessage(text="Выберите обращение"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"),2))]
            return list_answer

    def start_get_last_conversations(self, sender):
        job_itilium = JobItilium()
        list = job_itilium.get_last_conversations(sender)

        if len(list) == 0:
            return [TextMessage(text="Нет сообщений за последние 5 дней"), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            started_action = StartedAction(sender, "GetLastConversations", {"number": 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [TextMessage(text="Выберите сообщение для уточнения или просмотра"), KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list,
                                                                              started_action.additional.get("number"), 2))]
            return list_answer



    def on_command_select(self, message: str, sender: str):
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
        for i in list_actions_senders:
            if (isinstance(i, StartedAction)):
                if (i.sender == sender):
                    return i
        return None

    def sender_has_started_actions(self, sender: str):
        if (self.get_started_action(sender) == None):
            return False
        else:
            return True

    def remove_started_action(self, sender: str):
        for i in list_actions_senders:
            if (isinstance(i, StartedAction)):
                if (i.sender == sender):
                    list_actions_senders.remove(i)

    def continue_registration(self, message, sender: str):
        job_itilium = JobItilium()
        self.remove_started_action(sender)
        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel"):
            return [TextMessage(text="Регистрация отменена"), TemplatesKeyboards.get_keyboard_start_message()]
        else:
            return self.register_incident(job_itilium, message, sender)

    def continue_confirmed_input_comment(self, message, sender: str, started_action: StartedAction):
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

            started_action = StartedAction(sender, "Get_Comfirmed_input_comment",
                                           {"ref": reference_incident, "rating": rating})
            list_actions_senders.append(started_action)
            if need_comment:
                return [TextMessage(text="Данная оценка требует комментарий:"),
                        TemplatesKeyboards.get_keyboard_cancel_confirm()]
            else:
                return [TextMessage(text="Укажите комментарий к оценке"),
                        TemplatesKeyboards.get_keyboard_cancel_or_continue_withont_comment()]

    def continue_confirmed_select_buttons(self, message, sender: str, started_action: StartedAction):
        command = self.get_text_comand(message)
        reference_incident = started_action.additional
        self.remove_started_action(sender)
        if (command == "_Itilium_bot_Confirm"):
            job_itilium = JobItilium()
            rating_state = job_itilium.get_rating_for_incidents_confirmation(sender, reference_incident)
            print_value(rating_state.need_rating)
            if rating_state.need_rating:
                started_action = StartedAction(sender, "Get_Comfirmed_select_rating",
                                               {"ref": reference_incident, "rating_state": rating_state})
                list_actions_senders.append(started_action)
                return [ TextMessage(text="Оцените выполнение обращения"), TemplatesKeyboards.get_keyboard_rating()]
            elif rating_state.rating_exist:
                started_action = StartedAction(sender, "Get_Comfirmed_select_rating",
                                               {"ref": reference_incident, "rating_state": rating_state})
                list_actions_senders.append(started_action)
                return [TextMessage(text="Оцените выполнение обращения"), TemplatesKeyboards.get_keyboard_rating_with_continue()]
            else:
                job_itilium = JobItilium()
                answer = job_itilium.confirm_incident(sender, reference_incident, -1, "")
                if (answer == False):
                    return [TextMessage(text="Не удалось подтвердить обращение по причине:" + answer.description)]
                else:
                    return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]

        elif command == "_Itilium_bot_Decline":
            job_itilium = JobItilium()
            answer = job_itilium.decline_incident(sender, command)
            if (answer == False):
                return [TextMessage(text="Не удалось отклонить обращение по причине:" + answer.description),
                        TemplatesKeyboards.get_keyboard_start_message()]
            else:
                return [TextMessage(text=answer.description), TemplatesKeyboards.get_keyboard_start_message()]

        else:  # cancel
            return [TextMessage(text="Подтверждение не выполнено:"), TemplatesKeyboards.get_keyboard_start_message()]

    def continue_get_last_conversations_select_actions(self, message, sender: str, started_action: StartedAction):
        reference = started_action.additional
        self.remove_started_action(sender)
        command = self.get_text_comand(message)
        if command == "_Itilium_bot_get_conversations_modify":
            started_action = StartedAction(sender, "AddConversationsInputText", reference)
            list_actions_senders.append(started_action)
            return [TextMessage(text="Введите уточнение"),
                    TemplatesKeyboards.get_keyboard_cancel_modify()]

        elif command == "_Itilium_bot_get_conversations_close":
            return [TemplatesKeyboards.get_keyboard_start_message()]



    def continue_get_last_conversations(self, message, sender: str, started_action: StartedAction):
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)

        if (command == "_Itilium_bot_cancel_modify"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction(sender, "GetLastConversations",
                                           {"number": number_page + 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1, 2))]

            return list_answer
        else:
            started_action = StartedAction(sender, "GetLastConversation_select_action", command)
            list_actions_senders.append(started_action)
            detail_view = ""
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    break
            return [TextMessage(text="Детальная информация:"), TextMessage(text=detail_view),
                    TemplatesKeyboards.get_keyboard_on_show_conversation()]



    def continue_get_confirmed_select_incident(self, message, sender: str, started_action: StartedAction):
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel_confirmation"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction(sender, "GetConfirmedSelectIncident",
                                           {"number": number_page + 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1,2))]

            return list_answer
        else:
            started_action = StartedAction(sender, "GetConfirmed_SelectButtonsConfirmDecline", command)
            list_actions_senders.append(started_action)
            detail_view = ""
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    break
            return [TextMessage(text="Подтвердите или отклоните выполнение обращения:"), TextMessage(text=detail_view),
                    TemplatesKeyboards.get_keyboard_confirm()]

    def continue_get_state_select_incident(self, message, sender, started_action: StartedAction):
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        self.remove_started_action(sender)

        command = self.get_text_comand(message)
        if (command == "_Itilium_bot_cancel_modify"):
            return [TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            started_action = StartedAction(sender, "GetStateSelectIncident",
                                           {"number": number_page + 1, "list": list})
            list_actions_senders.append(started_action)
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
        list = started_action.additional.get("list")
        number_page = started_action.additional.get("number")
        command = self.get_text_comand(message)

        if (command == "_Itilium_bot_cancel_modify"):
            self.remove_started_action(sender)
            return [TextMessage(text="Уточнения не внесены"), TemplatesKeyboards.get_keyboard_start_message()]
        elif command == "_Itilium_bot_more_incidents":
            self.remove_started_action(sender)
            started_action = StartedAction(sender, "AddConversationsSelectIncident",
                                           {"number": number_page + 1, "list": list})
            list_actions_senders.append(started_action)
            list_answer = [KeyboardMessage(
                keyboard=TemplatesKeyboards.get_keyboard_select_incident_text(list, number_page + 1,2))]

            return list_answer
        else:
            self.remove_started_action(sender)
            started_action = StartedAction(sender, "AddConversationsInputText", command)

            detail_view = ""
            found = 0
            for wrapper in list:
                if (wrapper.id == command):
                    detail_view = wrapper.detail_view
                    found = 1
                    break
            if (found == 1):
                list_actions_senders.append(started_action)
                return [TextMessage(text="Введите уточнение:"), TextMessage(text=detail_view),
                        TemplatesKeyboards.get_keyboard_cancel_modify()]
            return self.get_start_message_answer()  # Не то ввел пользователь. Сначала

    def continue_add_conversations_input_text(self, message, sender: str, started_action: StartedAction):
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

    def continue_started_process(self, message, sender: str):
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
        else:
            return [TextMessage(text="Не реализовано "), TemplatesKeyboards.get_keyboard_start_message()]

    def get_text_comand(self, message):
        return GetTextCommand(message)

    def first_level_comand(self, message, sender: str):
        text = self.get_text_comand(message)
        if (self.is_start_message(text)):
            return self.get_start_message_answer()
        else:
            return self.on_command_select(text, sender)

    def process(self, message, sender: str):
        if (self.sender_has_started_actions(sender) == False):
            return self.first_level_comand(message, sender)
        else:
            return self.continue_started_process(message, sender)


class Integration:
    def on_new_message(self, message, sender: str):
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



is_registration = [False]
def GetIsRegistration():
    return is_registration[0]

def SetIsRegistration(state:bool):
    is_registration[0] = state


def VerifyRegistration(senderid, message ):
    job_itilium = JobItilium()
    if GetIsRegistration() == False:
        answer = job_itilium.not_exist(senderid)
        if answer.status:
            if (answer.result == str(1)):
                ret = TextMessage(text="Укажите свой номер телефона в формате +7хххххххххх")
                SetIsRegistration(True)
                return True, ret
            else:
                return False, None
        else:
            ret = TextMessage(text=answer.description)
            return True, ret
    elif GetIsRegistration() == True:
        answer = job_itilium.register(senderid, message)
        if answer.status == True:
            if (answer.result == str(1)):
                SetIsRegistration(False)
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


@app.route('/', methods=['POST'])
def incoming():
    logger.debug("received request. post data: {0}".format(request.get_data()))
    # every viber message is signed, you can verify the signature using this method
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    # this library supplies a simple way to receive a request object
    viber_request = viber.parse_request(request.get_data())

    integration = Integration()

    if isinstance(viber_request, ViberMessageRequest):

        isReg, mess = VerifyRegistration(viber_request.sender.id, viber_request.message)
        if isReg:
            viber.send_messages(viber_request.sender.id, mess)
        else:
            viber.send_messages(viber_request.sender.id, integration.on_new_message(viber_request.message, viber_request.sender.id))

    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.sender.id, integration.on_subscribe(viber_request.sender.id))
    elif isinstance(viber_request, ViberFailedRequest):
        integration.on_failed_message(viber_request.message, viber_request.sender.id)

    return Response(status=200)

# integration = Integration()
# senderid = "RH2xtdiCKsztWpOkGlMxZQ=="
########################################################################################################################
##          TESTS                                                            ###########################################
########################################################################################################################

_AddressApiItilium = "http://demo.desnol.ru/suhov_itil/hs/viberapi/action"
_LoginItilium = "admin"
_PasswordItilium = "1Q2w3e4r5t"

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
    print_value("VerifyRegistration begin")
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

def tests():
    test_non_exist()
    test_register()
    test_VerifyRegistration()

tests()