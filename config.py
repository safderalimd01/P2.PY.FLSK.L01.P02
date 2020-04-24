import mysql.connector


def fn_connect_db():
    try:
        config = {
            'user': 'root',
            'password': 'Arun@123',
            'host': 'localhost',
            'database': 'tansy_cloud'
        }

        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as error:
        return str(error)
