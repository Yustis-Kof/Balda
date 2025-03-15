from app.database import get_db_connection

def check_word(word):
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            sql = "SELECT * FROM dictionary WHERE word = %s"
            cursor.execute(sql, (word,))
            result = cursor.fetchone()
            return result is not None
    finally:
        connection.close()