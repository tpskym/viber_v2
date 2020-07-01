import os
import time
import random
import datetime
import requests
import logging
from flask import Flask, request, Response
import psycopg2

import json

app = Flask(__name__)
    
    
@app.route('/', methods=['GET'])
def incomingGet():

    print("begin")
    list = request.data.decode('utf-8')

    DATABASE_URL = os.environ['DATABASE_URL']
    print("database get")
    # Connect to an existing database
    conn = psycopg2.connect(DATABASE_URL, sslmode='require')
    print("con create")
    # Open a cursor to perform database operations
    cur = conn.cursor()
    print("Query exec")

    try:
        ret = ""
        cur.execute("SELECT * FROM data_saved")
        print("selkect from ")
        # Make the changes to the database persistent
        if cur.rowcount > 0:
            result_query = cur.fetchone()
            ret = result_query[1]
            ret = ret.replace("ghbdtnvbksqxtkjdt'nfcnhjrfxnj,sYbrnjktdsqytgbcfkc.lfybxtujrhjvtye;yjujntrcnf", "ttt")
        conn.commit()
        print("close conn")
        # Close communication with the database
    except Exception as e:
        print("Error:" + e.args[0])
        return "error"
    finally:
        cur.close()
        conn.close()
        print("close all")

    return ret

class instrument (object):
    id = ''
    name_value = ''
    currency_value = ''
    info_load_text = ''
    
    def remove_by_id(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("DELETE FROM instruments WHERE id = %s", ( self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
                
    def add_to_data_base(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("INSERT INTO instruments (name_value, currency_value, info_load) VALUES (%s, %s, %s)", ( self.name_value, self.currency_value, self.info_load_text))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
        
    def change_to_data_base(self): 
        self.create_table_if_need()   
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("UPDATE instruments SET name_value = %s, currency_value = %s, info_load = %s WHERE id = %s", ( self.name_value, self.currency_value, self.info_load_text, self.id));

            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
    def get_instrument_from_list(self, list_instrument, instrument_id):
        instr_find = False
        instrument_value = instrument()
        for instr in list_instrument:
            if instr.id == instrument_id:
                instrument_value = instr
                instr_find = True
                break
                
        if instr_find == False:
            print("instrument with id " +str(instrument_id) + " not found!!!")
        return instrument_value            
        
    def load_all(self):
        try:
            self.create_table_if_need()
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("SELECT * FROM instruments",)
            result = []
            if cur.rowcount > 0:
                while  cur.fetchone() :
                    instr = instrument()
                    instr.id = cur[0]
                    instr.name_value = cur[1]
                    instr.currency_value = cur[2]
                    instr.info_load_text = cur[3]
                                        
                    result.append(instr)
                
            # Make the changes to the database persistent
            conn.commit()

            # Close communication with the database
            return result
        except Exception as e:
            print("Error:" + e.args[0])
            return []
        finally:
            cur.close()
            conn.close()
            
        pass
        
    def load(self, id):
        list = self.get_all()
        if len(list) > 0 :
            for instr in list :
                if instr.id == id:
                    self.id = id
                    self.name_value = instr.name_value
                    self.currency_value = instr.currency_value
                    self.info_load_text = instr.info_load_text
                    
                    return True
            return False
        else:
            return False
        pass
    
    def create_table_if_need(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("select * from information_schema.tables where table_name=%s", ('instruments',))
            print("Query exec")
            if (cur.rowcount == 0):
                # Execute a command: this creates a new table
                cur.execute(
                    "CREATE TABLE instruments (id serial PRIMARY KEY, name_value text, currency_value text, info_load text );")
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            
            return False
        finally:
            cur.close()
            conn.close()
            
            
    
        
class last_data (object):
    id = ''
    instrument = instrument()
    price_sell = 0
    
    def remove_by_id(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("DELETE FROM last_data WHERE id = %s", ( self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
    
    def add_or_change_to_data_base(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            list_last_data = self.load_all()
            last_data = self.get_last_data_from_list(list_last_data, self.instrument.id)
            if last_data.instrument.id == '':
                cur.execute("INSERT INTO last_data (instrument_id, price_sell) VALUES (%s, %s)", ( self.instrument.id, self.price_sell))
            else:
                cur.execute("UPDATE last_data set instrument_id =%s, price_sell=%s where id=%s ", ( self.instrument.id, self.price_sell, self.id))
                                
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
    
    def load_all(self):
        try:
            self.create_table_if_need()
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("SELECT * FROM (last_data)",)
            result = []
            if cur.rowcount > 0:

                instrument_list = instrument().get_all()
                               
                while cur.fetchone():
                    current_last_data = last_data()
                    current_last_data.id = cur[0]
                    instrument_id = cur[1]
                    instrument_value = instrument().get_instrument_from_list(instrument_list, instrument_id)
                            
                    current_last_data.price_sell = cur[2]
                    current_last_data.instrument = instrument_value
                    result.append(current_last_data)

            # Make the changes to the database persistent
            conn.commit()

            # Close communication with the database
            return result
        except Exception as e:
            print("Error:" + e.args[0])
            return []
        finally:
            cur.close()
            conn.close()
            
    
    def get_last_data_from_list(self, instrument_id):
        list = self.load_all()
        last_data_value_ret = last_data()
        for last_data_value in list:
            if last_data_value.instrument.id == instrument_id:
                last_data_value_ret.id = last_data_value.id
                last_data_value_ret.instrument = last_data_value.instrument
                last_data_value_ret.price_sell = last_data_value.price_sell
                return last_data_value_ret
        return last_data_value_ret
            
                        
    def create_table_if_need(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("select * from information_schema.tables where table_name=%s", ('last_data',))
            print("Query exec")
            if (cur.rowcount == 0):
                # Execute a command: this creates a new table
                cur.execute(
                    "CREATE TABLE last_data (id serial PRIMARY KEY, instrument_id text, price_sell real );")
            return True    
            
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()

class work_in_job (object):
    id = ''
    instrument = instrument()
    price_buy = 0
    tp_value = 0
    count_buy = 0
    comission=0
    date=0
    
    sum_buy = 0    
    current_result_procent = 0    
    comission_sell = 0
    last_price=0
    last_summ_sell=0
    cur_profit=0
    
    def remove_by_id(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("DELETE FROM in_job WHERE id = %s", ( self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
    
    def add_to_data_base(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("INSERT INTO in_job (instrument_id , price_buy , count_buy , tp_value , comission , date ) VALUES (%s, %s, %s,%s, %s, %s)", ( self.instrument.id, self.price_buy, self.count_buy, self.tp_value, self.comission, self.date))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
        
    def change_to_data_base(self): 
        self.create_table_if_need()   
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("UPDATE in_job SET instrument_id=%s , price_buy=%s , count_buy=%s , tp_value=%s , comission=%s , date=%s WHERE id = %s", ( self.instrument.id, self.price_buy, self.count_buy, self.tp_value, self.comission, self.date, self.id));

            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()

    def get_work_from_list(self, list, id):
         for work in list:
             if work.id == id:
                 return work
         print("work with id " + str(id) + " not found!!!")        
         return work_in_job()
                                    
    def load_all(self, id):
        try:
            self.create_table_if_need()
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("SELECT * FROM (in_job)",)
            result = []
            if cur.rowcount > 0:
                list_instrument = intrument().get_all()
                list_last_data = last_data().load_all()
                while cur.fetchone():
                    instrument_id = cur[1]
                    in_job = work_in_job()
                    in_job.id = cur[0]
                    instrument_value = instrument().get_instrument_from_list(list_instrument, instrument_id)
                    
                    last_data_value = last_data().get_last_data_from_list(list_last_data, instrument_id)
                    
                    in_job.instrument = instrument_value
                                        
                    in_job.price_buy = cur[2]
                    in_job.tp_value = cur[4]
                    in_job.count_buy = cur[3]
                    in_job.comission=cur[5]
                    in_job.date=cur[6]
                    in_job.last_price=last_data_value.price_sell
                    in_job.sum_buy = in_job.price_buy * in_job.count_buy
                    in_job.last_summ_sell=last_data_value.price_sell * count_buy
                    
                    in_job.comission_sell = in_job.last_summ_sell * in_job.comission / in_job.sum_buy
                    
                    in_job.cur_profit=in_job.last_summ_sell - in_job.sum_buy - in_job.comission_sell - in_job.comission
                    
                
                    if in_job.sum_buy>0:                
                        in_job.current_result_procent=100*(in_job.last_summ_sell - in_job.comission_sell)/(in_job.sum_buy + in_job.comission)  - 100                   
                        
                    else:
                        in_job.current_result_procent =  0
                          
                    
                                        
    
                    result.append(in_job)
            # Make the changes to the database persistent
            conn.commit()

            # Close communication with the database
            return result
        except Exception as e:
            print("Error:" + e.args[0])
            return []
        finally:
            cur.close()
            conn.close()
            
        
    def create_table_if_need(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("select * from information_schema.tables where table_name=%s", ('in_job',))
            print("Query exec")
            if (cur.rowcount == 0):
                # Execute a command: this creates a new table
                cur.execute(
                    "CREATE TABLE in_job (id serial PRIMARY KEY, instrument_id text, price_buy real, count_buy real, tp_value real, comission real, date time );")
            return True    
            
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()

class sell():
    id = ''
    work_in_job=work_in_job()
    count_sell = 0
    price_sell=0
    comission_sell=0    
    date=0

    instrument = instrument()
    comission=0    
    price_buy = 0
    tp_value = 0    
    summ_buy=0
    result_procent = 0    
    summ_sell=0    
    cur_profit=0
    
    def remove_by_id(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("DELETE FROM sells WHERE id = %s", ( self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
    
    def truncate(self):
        self.create_table_if_need()
        list = self.load_all()
        summ = 0
        for item in list:
            summ = summ + item.cur_profit
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()            
            cur.execute("TRUNCATE sells")
            # in reports already saved
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                    
            
    
    def add_to_data_base(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("INSERT INTO sells (work_in_job_id , count_sell , price_sell , comission_sell, date) VALUES (%s, %s, %s, %s,%s %s )", (  self.work_in_job.id, self.count_sell, self.price_sell, self.comission_sell, self.date))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                
        
    def change_to_data_base(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("UPDATE sells  SET  work_in_job_id=%s , count_sell=%s , price_sell=%s , comission_sell=%s, date=%s) WHERE id=%s", (  self.work_in_job.id, self.count_sell, self.price_sell, self.comission_sell, self.date, self.id))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
                        
        
    def get_sell_in_list(self, list, id):
        for item in list:
            if item.id == if:
                return item
        print("sell with id "+ id + " not found!!!")
        return sell()
    
    def load_all(self):
        try:
            self.create_table_if_need()
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("SELECT * FROM (sells)",)
            result = []
            if cur.rowcount > 0:
        
                instrument_list = instrument().get_all()
                work_list = work_in_job().load_all()               
                
                while cur.fetchone():
                    sell_value = sell()
                    sell_value.id = cur[0]
                    
                    instrument_id = cur[1]
                    
                    instrument_value = instrument().get_instrument_from_list(instrument_list, instrument_id)
                    
                    work_id = cur[2]
                    
                    work_value = work_in_job().get_work_from_list(work_list, work_id)
                    
                    sell_value.count_sell = cur[3]
                    sell_value.price_sell = cur[4]                    
                    sell_value.comission_sell = cur[5]
                    sell_value.date = cur[6]
                    sell_value.instrument = instrument_value
                    sell_value.work_in_job = work_value
                    if work_value.count_buy > 0:
                        teil = sell_value.count_sell / work_value.count_buy
                    else:
                        teil = 0  
                    sell_value.comission=work_value.comission*teil    
                    sell_value.price_buy = work_value.price_buy
                    sell_value.tp_value = work_value.tp_value    
                    sell_value.summ_buy=work_value.sum_buy*teil
                        
                    sell_value.summ_sell=sell_value.count_sell * sell_value.price_sell    
                    if sell_value.summ_buy > 0:
                        sell_value.result_procent = 100*(sell_value.summ_sell - sell_value.comission_sell)/(sell_value.summ_buy + sell.comission) - 100    
                    else:
                        sell_value.result_procent = 0
                    
                    
                    
                    sell_value.cur_profit=sell_value.summ_sell - sell_value.summ_buy - sell_value.comission - sell_value.comission_sell
                                        
                    result.append(sell_value)
        
            # Make the changes to the database persistent
            conn.commit()
        
            # Close communication with the database
            return result
        except Exception as e:
            print("Error:" + e.args[0])
            return []
        finally:
            cur.close()
            conn.close()
            
    
    def create_table_if_need(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("select * from information_schema.tables where table_name=%s", ('sells',))
    
            if (cur.rowcount == 0):
                # Execute a command: this creates a new table
                cur.execute(
                    "CREATE TABLE sells (id serial PRIMARY KEY, instrument_id text, work_in_job_id text, count_sell real, price_sell real, comission_sell real, date time );")
            return True    
            
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()

class result_work():
    id = ''
    list = []
    start_summ_sells = 0

    def remove_by_id(self):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("DELETE FROM results_work WHERE id = %s", ( self.id,))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
    
    def load_all(self):                        
        try:
            self.create_table_if_need()
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("SELECT * FROM (results_work)",)
            result = []
            if cur.rowcount > 0:

                while cur.fetchone():
                    result_work_value = result_work()
                    result_work_value.id = cur[0]
                    result_work_value.date = cur[1]
                    result_work_value.summ = cur[2]
                    result_work_value.comission= cur[3]

                    result.append(result_work_value)

            # Make the changes to the database persistent
            conn.commit()

            # Close communication with the database
            return result
        except Exception as e:
            print("Error:" + e.args[0])
            return []
        finally:
            cur.close()
            conn.close()
            

    def add_sell_result(self, date, profit, comission):
        self.create_table_if_need()
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            
            cur.execute("INSERT INTO results_work (date , summ , comission ) VALUES (%s, %s, %s )", ( date, profit, comission))
            conn.commit()
            return True
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()
          
       
    def create_table_if_need(self):
        try:
            DATABASE_URL = os.environ['DATABASE_URL']
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            # Open a cursor to perform database operations
            cur = conn.cursor()
            cur.execute("select * from information_schema.tables where table_name=%s", ('results_work',))
    
            if (cur.rowcount == 0):
                # Execute a command: this creates a new table
                cur.execute(
                    "CREATE TABLE results_work (id serial PRIMARY KEY, date time, summ real, comission real );")
            return True    
            
        except Exception as e:
            print("Error:" + e.args[0])
            return False
        finally:
            cur.close()
            conn.close()        
    
class work_with_sell():
    def add_sell_from_work(id_work, count_sell, price_sell, comission_sell, date):
        sell_value = sell()
        sell_value.instrument.id = 
        
        pass
        

class tests():
    def instrument_equals_ref(self, instrument_value_one, instrument_value_two):
        return self.instrument_equals(instrument_value_one, instrument_value_two.name_value, instrument_value_two.currency_value, instrument_value_two.info_load_text)
        
    def instrument_equals(self, instrument_value, name_value, currency_value, info_load_value):
        if instrument_value.name_value == name_value and instrument_value.currency_value == currency_value and instrument_value.info_load_value = info_load_value:
            return True
        else:
            return False
                     

    def instruments(self):
        instrument_value = instrument()   
        instrument_value.name_value = 'test_name_instrument'
        instrument_value.currency_value = 'test_currrency' 
        instrument_value.info_load_text = 'test_info_load_text'
        if instrument_value_new.add_to_data_base():
            print("instrument.add_to_data_base OK")
        else:
            print("instrument.add_to_data_base ERROR")    
                        
        instrument_value_new = instrument()
        instrument_value_new.name_value = 'test_name_instrument_new'
        instrument_value_new.currency_value = 'test_currrency_new' 
        instrument_value_new.info_load_text = 'test_info_load_text_new'
        if instrument_value_new.add_to_data_base():
            print("instrument.add_to_data_base 2 OK")
        else:
            print("instrument.add_to_data_base 2 ERROR")    
            
        list_instrument_value_load = instrument().load_all()
        if len(list) == 2:
            print ("instrument.load_all() size OK")
        else:
            print ("instrument.load_all() size ERROR")
            
        if self.instrument_equals(list_instrument_value_load[0], "test_name_instrument", "test_currrency", "test_info_load_text"):
            print("instrument.load_all 0 OK")
        else:
            print("instrument.load_all 0 ERROR")
            
        if self.instrument_equals(list_instrument_value_load[1], "test_name_instrument_new", "test_currrency_new", "test_info_load_text_new"):
            print("instrument.load_all 1 OK")
        else:
            print("instrument.load_all 1 ERROR")
                            
        loaded_instrument_by_id = instrument().load(list_instrument_value_load[0].id)

        loaded_instrument_by_id_two = instrument().load(list_instrument_value_load[1].id)

        loaded_instrument_by_id_get = instrument().get_instrument_from_list(list_instrument_value_load, list_instrument_value_load[1].id)


        if self.instrument_equals_ref(loaded_instrument_by_id, list_instrument_value_load[0])
            print("instrument.load 0 OK" )
        else:
            print("instrument.load 0 ERROR" )
            
        if self.instrument_equals_ref(loaded_instrument_by_id_two, list_instrument_value_load[1])
            print("instrument.load 1 OK" )
        else:
            print("instrument.load 1 ERROR" )

        if self.instrument_equals_ref(loaded_instrument_by_id_two, loaded_instrument_by_id_get)
            print("instrument.load 2 OK" )
        else:
            print("instrument.load 2 ERROR" )
                        
        instrument_changed = list_instrument_value_load[0]
        instrument_changed.name_value = "name_changed"
        instrument_changed.currency_value = "currency_changed"
        instrument_changed.info_load_text = "info_load_changed"
        if instrument_changed.change_to_data_base():
            print ("instrument.change_to_data_base OK")
        else:
            print ("instrument.change_to_data_base ERROR")
            
        instr_changed_loaded = instrument().load(instrument_changed.id)
        
        if self.instrument_equals_ref(instr_changed_loaded, instrument_changed)
            print("instrument.change_to_data_base load  OK" )
        else:
            print("instrument.change_to_data_base  ERROR" )        
            
        if instrument().remove_by_id(list_instrument_value_load[0]):
            print("instrument.remove_by_id OK")
        else:
            print("instrument.remove_by_id ERROR")       
             
        new_list = instrument.load_all()
        if len(new_list) == 1:
            print("instrument.remove_by_id len OK")
        else:
            print("instrument.remove_by_id len ERROR")
            
        if self.instrument_equals_ref(new_list[0], list_instrument_value_load[1])
            print("instrument.remove_by_id equals OK")
        else:
            print("instrument.remove_by_id equals ERROR")
             
        
        

@app.route('/set/in_job/', methods=['POST'])
def incoming_set_in_job():
    try:
        data_str = request.data.decode('utf-8')
        work = work_api()
        work.set_in_job(data_str)        
        return 'it works'
    except Exception as e:
        return "it works good"
         

@app.route('/', methods=['POST'])
def incoming():
    try:
        print("begin")
        list = request.data.decode('utf-8')

        print("data readed")
        if (list.find("ghbdtnvbksqxtkjdt'nfcnhjrfxnj,sYbrnjktdsqytgbcfkc.lfybxtujrhjvtye;yjujntrcnf") == -1):
            print("not found key - return")
            return ""

        DATABASE_URL = os.environ['DATABASE_URL']
        print("database get")
        # Connect to an existing database
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')
        print("con create")
        # Open a cursor to perform database operations
        cur = conn.cursor()
        print("Cursor create")
        cur.execute("select * from information_schema.tables where table_name=%s", ('data_saved',))
        print("Query exec")
        if (cur.rowcount == 0):
            # Execute a command: this creates a new table
            print("Первый запуск. Создание таблиц  data_saved")
            cur.execute(
                "CREATE TABLE data_saved (id serial PRIMARY KEY, message_id text );")


        cur.execute("TRUNCATE data_saved");
        print("TRUNCATE table")
        try:
            cur.execute("INSERT INTO data_saved (message_id) VALUES (%s)",
                        (list,))
            print("insert in table")
            # Make the changes to the database persistent
            conn.commit()
            print("close conn")
            # Close communication with the database
        except Exception as e:
            print("Error:" + e.args[0])
            return "error"
        finally:
            cur.close()
            conn.close()
            print("close all")
        print("is Ok")
        return ""

    except Exception as e:
        print("errors:" + e.args[0])
        return "error"
