import os
import psycopg2
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.keyboard_message import KeyboardMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
import requests
import logging
from flask import Flask, request, Response

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest
import json


#DATABASE_URL = os.environ['DATABASE_URL']
# Connect to an existing database
#conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Open a cursor to perform database operations
#cur = conn.cursor()

# Execute a command: this creates a new table
#cur.execute("CREATE TABLE test (id serial PRIMARY KEY, num integer, data varchar);")

# Pass data to fill a query placeholders and let Psycopg perform
# the correct conversion (no more SQL injections!)
#cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)",
#...      (100, "abc'def"))

# Query the database and obtain data as Python objects
#cur.execute("SELECT * FROM test;")
#cur.fetchone()
#(1, 100, "abc'def")

# Make the changes to the database persistent
#conn.commit()

# Close communication with the database
#cur.close()
#conn.close()
app = Flask(__name__)
@app.route('/',  methods=['POST'])
def incoming():
    print("Hello World")

    
    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())
    
    if isinstance(viber_request, ViberMessageRequest):
        print("Hello World")
        
    return Response(status=200)

