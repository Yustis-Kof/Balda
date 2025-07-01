from app import create_app
from app.utils.dictionary import get_db_connection

app = create_app()

if __name__ == '__main__':
    nouns = open("nouns.txt", "r", encoding="utf-8").read()
    connection = get_db_connection()
    with connection.cursor() as cursor:
        sql = "INSERT INTO `dictionary` VALUES (NULL, %s)"
        for noun in nouns.split('\n'):
            cursor.execute(sql, (noun))
            print(cursor.fetchall())
        connection.commit()