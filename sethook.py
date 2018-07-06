
# from viberbot import Api
# from viberbot.api.bot_configuration import BotConfiguration
# auth_token_out = '4807270b7ee7d14d-fa37d43de286a0ef-be81bbab61de274b'
# viber = Api(BotConfiguration(
#     name='Itilium-bot',
#     avatar='http://site.com/avatar.jpg',
#     auth_token=auth_token_out
# ))
# viber.unset_webhook()
# viber.set_webhook("https://botitilium.herokuapp.com/")

import json
import requests

AddressApiItilium = 'http://demo.desnol.ru/suhov_itil/hs/viberapi/action'
LoginItilium = 'admin'
PasswordItilium = '1Q2w3e4r5t'

def print_value(object_to_print, value: str = "-----------------------------"):
    print(value + "{}".format(object_to_print))


def print_debug(value):
    print_value(value)


class Answer:

    status: bool = True
    result = ""
    description: str = ""

class JobItilium:

    def get_state(self, environ,  sender):
        print_debug("def get_state")
        quote = "\""
        data_to_send = """{
                                                        "data": {
                                                        "action": "get_state",
                                                        "type": """ + quote + environ + quote + """,
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
            if description == "":
                answer.result = ""
            else:
                answer.result = json.loads(description)
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer

    def set_state(self, sender, environ,  state):
        print_debug("def get_state")
        quote = "\""
        data_to_send = json.dumps({ "data" : {
            "action" : "set_state",
            "sender" : sender,
            "type": environ,
            "state" : state
        }})

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
            answer.result = ""
        else:
            answer.status = False
            answer.description = description + " ERROR CODE:" + str(code)
        return answer


class EmptyValue:
    empty = True


def SaveValueToEnviron(value, NameEnviron, sender):
    job = JobItilium()
    answer = job.set_state(sender, NameEnviron, value)
    if answer.status:
        return True, ""
    else:
        return False, answer.description




def LoadValueFromEnviron(NameEnviron, sender):
    job = JobItilium()
    answer = job.get_state(NameEnviron, sender)
    if answer.status:
        data = answer.result
        if data == "":
            return True, EmptyValue()
        else:
            return True, data
    else:
        return False, answer.description

environ = "test_environ"
SaveValueToEnviron({"name":"alefffx", "data": "simpdddle data"} ,environ , "123")
state, res = LoadValueFromEnviron(environ, "123")
print_debug(res)