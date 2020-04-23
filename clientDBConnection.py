import flask
import functools

from resources.db.dbConnect import fn_connect_client_db
from resources.utils.crypto.crypto import fn_decrypt


def fn_make_client_db_connection():
    """
    check db connection
    """
    def decorator(function):
        @functools.wraps(function)
        def wrapper(request, *args, **kwargs):
            encrypt_db_user = flask.request.headers.get('encrypt_db_user')
            encrypt_db_pwd = flask.request.headers.get('encrypt_db_pwd')
            encrypt_db_host = flask.request.headers.get('encrypt_db_host')
            encrypt_db_database = flask.request.headers.get('encrypt_db_database')

            db_name, cursor_name = fn_decrypt(encrypt_db_database)
            db_user, cursor_user = fn_decrypt(encrypt_db_user)
            db_pwd, cursor_pwd = fn_decrypt(encrypt_db_pwd)
            db_host, cursor_host = fn_decrypt(encrypt_db_host)

            if cursor_name == 400 or cursor_user == 400 or cursor_pwd == 400 or cursor_host == 400:
                return { "args": {
                                "oparam_err_msg": "Invalid Credentials",
                                "oparam_login_success": 0,
                                "oparam_err_flag": 1
                            },
                           "status": "Failure",
                           "message": "Encrypted error"}, 400
            else:
                client_db_connection = fn_connect_client_db(user=db_user,
                                                            password=db_pwd,
                                                            database=db_name,
                                                            host=db_host)

                kwargs['client_db_connection'] = client_db_connection
                return function(request, *args, **kwargs)

        return wrapper
    return decorator

