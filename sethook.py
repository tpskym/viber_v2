
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
auth_token_out = ''
viber = Api(BotConfiguration(
     name='Itilium-bot',
     avatar='http://site.com/avatar.jpg',
     auth_token=auth_token_out
 ))
viber.unset_webhook()
viber.set_webhook("https://botitilium.herokuapp.com/")
