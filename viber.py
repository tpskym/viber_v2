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

def SaveStateToPostgress(sender_id, state_id, carousel_id, data_user, data):
    data_user_string = json.dumps(data_user)
    data_bot_string = json.dumps(data)
    state = True
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Open a cursor to perform database operations

        cur = conn.cursor()

        need_drop = True
        cur.execute("select * from information_schema.tables where table_name=%s", ('data_users',))
        if(cur.rowcount == 0):
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE data_users (id serial PRIMARY KEY, sender_id varchar(50), state_id varchar(36), carousel_id varchar(36),data_user text, data text );")
            need_drop = False

        if need_drop:
            cur.execute("DELETE FROM data_users WHERE sender_id = %s", (sender_id,));
        # Pass data to fill a query placeholders and let Psycopg perform
        # the correct conversion (no more SQL injections!)
        cur.execute("INSERT INTO data_users (sender_id, state_id, carousel_id, data_user, data) VALUES (%s, %s, %s, %s, %s)",
              (sender_id, state_id, carousel_id, data_user_string, data_bot_string))

        # Make the changes to the database persistent
        conn.commit()
        # Close communication with the database
    except:
        state = False
    finally:
        cur.close()
        conn.close()
    return state

def RestoreStateFromPostgress(sender_id):
    state = False
    is_error = False
    try:
        DATABASE_URL = os.environ['DATABASE_URL']
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        # Open a cursor to perform database operations
        cur = conn.cursor()

        cur.execute("select * from information_schema.tables where table_name=%s", ('data_users',))
        if(cur.rowcount == 0):
            # Execute a command: this creates a new table
            cur.execute("CREATE TABLE data_users (id serial PRIMARY KEY, sender_id varchar(50), state_id varchar(36), carousel_id varchar(36),data_user text, data text );")
            conn.commit()
            restore_ok = False

        if not restore_ok:
            return {'error': is_error, 'state' : False}
        cur.execute("SELECT sender_id,  state_id,  carousel_id, data_user,  data FROM data_users WHERE sender_id = %s", (sender_id,))
        result_query = cur.fetchone()
        if(not result_query == None):
            return {'state':True, 'sender_id':result_query[0], 'state_id':result_query[1], 'carousel_id':result_query[2],'data_user': json.loads(result_query[3]), 'data':json.loads(result_query[4])}
        else:
            return {'error': is_error, 'state' : False}

        # Make the changes to the database persistent

        # Close communication with the database
    except:
        is_error = True
        restore_ok = False
    finally:
        cur.close()
        conn.close()
    return {'error': is_error, 'state' : state}



app = Flask(__name__)

@app.route('/register',  methods=['GET'])
def incomingGET():
    text = request.url
    return text

@app.route('/',  methods=['GET'])
def incomingGET():
    text = request.url
    # DATABASE_URL = os.environ['DATABASE_URL']
    # text = "empty"
    # # Connect to an existing database
    # conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    #
    #
    #
    #
    # # Open a cursor to perform database operations
    # cur = conn.cursor()
    # try:
    #     cur.execute("select * from information_schema.tables where table_name=%s", ('data_users',))
    #     if(cur.rowcount > 0):
    #         text = "exist_table"
    #     else:
    #         text = "NOT exist_table"
    #         # Execute a command: this creates a new table
    #         cur.execute("CREATE TABLE data_users (id serial PRIMARY KEY, sender_id varchar(50), state_id varchar(36), carousel_id varchar(36),data_user text, data text );")
    #         text += "\nTable created"
    #
    #
    #
    #     # Pass data to fill a query placeholders and let Psycopg perform
    #     # the correct conversion (no more SQL injections!)
    #
    #     cur.execute("INSERT INTO data_users (sender_id, state_id, carousel_id, data_user, data) VALUES (%s, %s, %s, %s, %s)",
    #           ("sender_id_test", "state_id_test", "carousel_id_test", "data_user", "data"))
    #     text += '\n' + "Add string"
    #     # Query the database and obtain data as Python objects
    #     cur.execute("SELECT sender_id,  state_id,  carousel_id, data_user,  data FROM data_users;")
    #     result_query = cur.fetchone()
    #     if(not result_query == None):
    #         text += '\n' + "sender_id: " + result_query[0]
    #         text += '\n' + "state_id: " + result_query[1]
    #         text += '\n' + "carousel_id: " + result_query[2]
    #         text += '\n' + "data_user: " + result_query[3]
    #         text += '\n' + "data: " + result_query[4]
    #     else:
    #         text += '\n' + "empty result"
    #
    #
    #     cur.execute("DELETE FROM data_users WHERE sender_id = %s", ("sender_id_test",));
    #     text += '\n' + "remove string"
    #
    #     cur.execute("SELECT sender_id,  state_id,  carousel_id, data_user,  data FROM data_users;")
    #     result_query = cur.fetchone()
    #     if(not result_query == None):
    #         text += '\n' + "sender_id: " + result_query[0]
    #         text += '\n' + "state_id: " + result_query[1]
    #         text += '\n' + "carousel_id: " + result_query[2]
    #         text += '\n' + "data_user: " + result_query[3]
    #         text += '\n' + "data: " + result_query[4]
    #     else:
    #         text += '\n' + "empty result"
    #
    #     # Make the changes to the database persistent
    #     conn.commit()
    #
    #     # Close communication with the database
    # finally:
    #     cur.close()
    #     conn.close()
    return text

@app.route('/',  methods=['POST'])
def incoming():
    print("Hello World")


    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())

    if isinstance(viber_request, ViberMessageRequest):
        print("Hello World")

    return Response(status=200)
