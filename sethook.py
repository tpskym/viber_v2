import json
import requests
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.rich_media_message import RichMediaMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.text_message import TextMessage

auth_token_out = '4807270b7ee7d14d-fa37d43de286a0ef-be81bbab61de274b'
viber = Api(BotConfiguration(
     name='Itilium-bot',
     avatar='http://site.com/avatar.jpg',
     auth_token=auth_token_out
 ))
# viber.unset_webhook()
# viber.set_webhook("https://botitilium.herokuapp.com/")
id = 'RH2xtdiCKsztWpOkGlMxZQ=='
SAMPLE_ALT_TEXT = "upgrade now!"

# list_answer = [TextMessage(text="Выберите обращение")].extend( [TextMessage(text="Выберите обращение"),TextMessage(text="Выберите обращение")] )
# list_answer = [TextMessage(text="Выберите обращение"),TextMessage(text="Выберите обращение")]



quote = "\""
response = requests.post('http://demo.desnol.ru/suhov_itil/hs/viberapi/action', data="""{
                                                    "data": {
                                                    "action": "register",
                                                    "sender": """ + quote + id + quote + """,
                                                    "phone":  """ + quote + '293' + quote + """,
                                                    }
                                                }""",
                         auth=('admin', '1Q2w3e4r5t'))
code = response.status_code
description = response.text


