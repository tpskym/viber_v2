
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

value = json.dumps([{'type': "jfjfjfjj", 'state': {'name': "aaaa"} }])
print (value)
obj = json.loads(value)
print(obj[0].get('state'))