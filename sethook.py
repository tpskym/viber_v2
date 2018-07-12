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

list_answer = [1]
list_answer.extend( [1,2] )
print("before list answer")
print("{}".format(list_answer))


# details = viber.get_user_details(id)
viber.send_messages(id, [TextMessage(text="привет"),
            RichMediaMessage(min_api_version=4, rich_media=
                {
                "Type": "rich_media",
                "BgColor": "#FFFFFF",
                "Buttons":[
                    {
                        "ActionBody":"454545454",
                        "ActionType":"reply",
                        "Text":"222222Очень длинный текст обращения, Очень длинный текст обращения, Очень длинный текст обращения, "
                    },
                    {
                        "ActionBody":"https://www.google.com",
                        "ActionType":"open-url",
                        "Text":"2S2hould get back my URL encoded ID instead of replace_me_with_url_encoded_receiver_id"
                    }]}),KeyboardMessage(min_api_version=4, keyboard={
            "Type": "keyboard",
            "InputFieldState": "hidden",
            "Buttons": [{
                "Columns": 6,
                "Rows": 1,
                "ActionBody": "_Itilium_bot_cancel",
                "Text": "Отменить подтверждение"
            }]
        })])

# viber.send_messages(id, [KeyboardMessage(min_api_version=4, keyboard={
#             "Type": "keyboard",
#             "InputFieldState": "hidden",
#             "Buttons": [{
#                 "Columns": 6,
#                 "Rows": 1,
#                 "ActionBody": "_Itilium_bot_cancel",
#                 "Text": "Отменить подтверждение"
#             }]
#         })])
