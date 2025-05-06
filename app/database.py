import pymysql
from config import Config

def get_db_connection():
    return pymysql.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

def authenticate_user(username, password):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, username FROM users WHERE username = %s AND password = %s"
            cursor.execute(sql, (username, password))
            return cursor.fetchone()
    finally:
        connection.close()

def get_random_word(dictionary="dictionary", length=5):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT word FROM %s WHERE LEN(word)=%s ORDER BY RAND() LIMIT 1"
            cursor.execute(sql, (dictionary, length))
            return cursor.fetchone()
    finally:
        connection.close()