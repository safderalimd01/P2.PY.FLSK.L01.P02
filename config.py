import mysql.connector


def fn_connect_db():
    try:
        config = {
            'user': 'root',
            'password': 'root',
            'host': '127.0.0.1',
            'database': 'tss'
        }

        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as error:
        return str(error)

