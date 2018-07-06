
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


class WrapperView:
    def __init__(self, view: str, detail_view: str, id: str):
        self.view = view
        self.id = id
        self.detail_view = detail_view

class Answer:
    def __init__(self, status = True, result = "", description = ""):
        self.status = status
        self.result = result
        self.description = description
    status: bool = True
    result = ""
    description: str = ""


answer = Answer(True, WrapperView("1","1","1"))
print(answer)