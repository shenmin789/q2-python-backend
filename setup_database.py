from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()
# Connection parameters and access credentials
host   = os.getenv("DB_HOST")  # MySQL server is running on local machine
user    = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
def create_connection(database=None):
    con = None
    try:
        if database is None:
            con = mysql.connector.connect(host=host, user=user, password=password)
        else:
            con = mysql.connector.connect(host=host, user=user, password=password, database=database)
        return con
    except Exception as e:
        print(e)

    return con

def create_user(cursor, user, password):
    try:
        sql = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';"%(user, password);
        cursor.execute(sql)
    except Exception as Ex:
        print("Error creating MySQL User: %s"%(Ex))

def create_db(conn, database_name):
    try:
        cur = conn.cursor()
        sql = "CREATE DATABASE IF NOT EXISTS "+database_name
        cur.execute(sql)
    except Exception as Ex:
        print("Error creating database: %s"%(Ex))

def exec_sql(conn, sql):
    try:
        cur = conn.cursor()
        cur.execute(sql)
    except Exception as Ex:
        print("Error creating table: %s"%(Ex))

if __name__ == '__main__':
    con = create_connection()
    create_db(con, 'test')
    con_mpk = create_connection('test')
    create_employee_table = "CREATE TABLE IF NOT EXISTS currency_insert_batches ("\
    "id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"\
    "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP);"
    exec_sql(con_mpk, create_employee_table)
    create_employee_table = "CREATE TABLE IF NOT EXISTS currency_conversion_rates ("\
    "id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,"\
    "batch_id INT,"\
    "name TEXT,"\
    "from_currency TEXT,"\
    "to_currency TEXT,"\
    "value DECIMAL(10,6),"\
    "created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,"\
    "FOREIGN KEY (batch_id) REFERENCES currency_insert_batches(id));"
    exec_sql(con_mpk, create_employee_table)
