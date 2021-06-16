from flask import Flask, request, jsonify, make_response, json
from flask_apscheduler import APScheduler
from flask_cors import CORS, cross_origin
from requests import get
from dotenv import load_dotenv
from itertools import chain, permutations
import mysql.connector
import decimal
import atexit
import time
import os

# set scheduler configuration values
class Config:
    SCHEDULER_API_ENABLED = True

class MyJSONEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)

load_dotenv()
app = Flask(__name__)
CORS(app)
app.json_encoder = MyJSONEncoder
app.config.from_object(Config())
app.config["DEBUG"] = True
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
scheduler = APScheduler()

#start methods
def get_mysql_conn():
    conn = None
    try:
        conn = mysql.connector.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USERNAME"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_DATEBASE"))
        return conn
    except Exception as e:
        print(e)
    return conn

def insert_currency_data():
    conn = get_mysql_conn()
    curr = conn.cursor()
    currencies = ["USD", "MYR", "EUR"]
    combination = list(permutations(currencies, 2))
    batch = ("INSERT INTO currency_insert_batches VALUES (DEFAULT, DEFAULT);")
    curr.execute(batch)
    batch_id = curr.lastrowid
    for i in range(0,len(combination),2):
        subset1 = list(combination[i])
        subset2 = list(combination[i+1])
        c1 = subset1[0]+"_"+subset1[1]
        c2 = subset2[0]+"_"+subset2[1]
        response = get(os.getenv("CURRENCY_CONVERTER_API_ADDRESS")+'/convert?apiKey='+os.getenv("CURRENCY_CONVERTER_API_KEY")+"&q="+c1+","+c2)
        json_res = response.json()

        print(json_res)
        for k, v in json_res['results'].items():
            name = v['id']
            from_currency = v['fr']
            to_currency = v['to']
            value = v['val']
            # print(v)
            # print(str(batch_id)+"|"+name+"|"+from_currency+"|"+to_currency+"|"+str(value))
            add_emp = ("INSERT INTO currency_conversion_rates "
            "(batch_id, name, from_currency, to_currency, value) "
            "VALUES (%s,%s,%s,%s,%s)")
            data_emp = (batch_id, name, from_currency, to_currency, value)
            curr.execute(add_emp, data_emp)

    conn.commit()
    curr.close()
    conn.close()

def get_currency_data():
    conn = get_mysql_conn()
    curr = conn.cursor(dictionary=True, buffered=True)
    curr.execute("SELECT * FROM currency_insert_batches ORDER BY created_at desc")
    latest_batch = curr.fetchone()

    curr.execute("SELECT * FROM currency_conversion_rates WHERE batch_id = %s", (latest_batch['id'],))
    currencies = curr.fetchall()
    return currencies


#end methods

#start routes
@app.route('/', methods=['GET'])
def home():
    return "<h1>TEST</p>"

@app.route('/currencies', methods=['GET'])
@cross_origin()
def currencies():
    if request.method == 'GET':
        data = get_currency_data()
        return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify({"message": "error"}), 400) 
#end routes

#start cron
@scheduler.task('cron', id='get_latest_currency_conversion', hour='23', minute='59')
def cron():
    insert_currency_data()
    print(time.strftime("%A, %d. %B %Y %I:%M:%S %p"))
#end cron

if __name__ == '__main__':

    # initialize scheduler
    scheduler.init_app(app)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    # initialize currency data for the first time
    insert_currency_data()
    app.run(host="localhost",port=8000, use_reloader=False)