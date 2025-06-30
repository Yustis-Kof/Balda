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

def get_random_word(dictionary="`dictionary`", length=5):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT word FROM `dictionary` WHERE LENGTH(word)=%s ORDER BY RAND() LIMIT 1" # аргумент dictionary пока не используем, потому что он вставляется вместе с одинарными кавычками
            cursor.execute(sql, (length*2))     # По какой-то причине 1 кириллический символ равен двум
            return cursor.fetchone()['word']
    finally:
        connection.close()

def add_user(username, password):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO `users` VALUES (NULL, %s, %s)"
            cursor.execute(sql, (username, password))
    finally:
        connection.close()

def get_user(id):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM `users` WHERE id=%s"
            cursor.execute(sql, (id))
            return cursor.fetchone()
    finally:
        connection.close()

def get_all_users():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, username FROM `users`"
            cursor.execute(sql)
            return cursor.fetchall()
    finally:
        connection.close()