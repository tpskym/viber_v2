
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

osenviron = {"state_users":""}

class StartedAction:
    def __init__(self, name: str, additional):
        self.name = name
        self.additional = additional
    def get_json(self):
        return json.dumps({"name": self.name, "additional": self.additional})

def SaveValueToEnviron(value, NameEnviron, sender):
    data = osenviron[NameEnviron]
    if data == "":
        osenviron[NameEnviron] = json.dumps([{"sender":sender,"state":value}])
        return
    else:
        data = json.loads(data)
        for senderid in data:
            if senderid.get("sender") == sender:
                senderid["state"] = value
                osenviron[NameEnviron] = json.dumps(data)
                return
        data.append({"sender":sender,"state": value})
        osenviron[NameEnviron] = json.dumps(data)


def LoadValueFromEnviron(NameEnviron, sender):
    data = osenviron[NameEnviron]
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

