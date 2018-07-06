
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
class WrapperView:

    def __dict__(self):
        return json.dumps({"view": self.view, "detail_view": self.detail_view,"id":self.id})

    def __init__(self, view: str, detail_view: str, id: str):
        self.view = view
        self.id = id

        self.detail_view = detail_view

json.dumps(WrapperView("1","1","1"))