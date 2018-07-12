import json
import requests
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.rich_media_message import RichMediaMessage
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
# viber.send_messages(id, RichMediaMessage(min_api_version=4, rich_media=
# {
#     "Type": "rich_media",
#     "BgColor": "#FFFFFF",
#     "Buttons":[
#              {
#                 "ActionBody":"454545454",
#                 "ActionType":"reply",
#                 "Text":"1Очень длинный текст обращения, Очень длинный текст обращения, Очень длинный текст обращения, "
#              },
#              {
#                 "ActionBody":"https://www.google.com",
#                 "ActionType":"open-url",
#                 "Text":"2S2hould get back my URL encoded ID instead of replace_me_with_url_encoded_receiver_id"
#              },
#              {
#                 "ActionBody":"https://www.google.com",
#                 "ActionType":"open-url",
#                 "Text":"4Should get back my name instead of replace_me_with_user_name"
#              },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "4Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "5Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "6Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "7Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "8Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "9Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "10Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "11Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "12Should get back my name instead of replace_me_with_user_name"
#             },
#             {
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "13Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "14Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "15Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "16Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "17Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "18Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "19Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "20Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "21Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "22Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "23Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "24Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "25Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "26Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "27Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "28Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "29Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "30Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "31Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "32Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "33Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "34Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "35Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "36Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "37Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "38Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "39Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "40Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "41Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#             },{
#                 "ActionBody": "https://www.google.com",
#                 "ActionType": "open-url",
#                 "Text": "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#                         "42Should get back my name instead of replace_me_with_user_name"
#             }
#
#
#           ]
# }) )
#

