import mysql.connector
import json
import os
import datetime
from resources.utils.serialize import clsCustomJSONEncoder

def fn_get_sproc_argnames(cursor, sproc_name):
    """ ordinary mysql cursor.callproc() won't give us argument names
        in mysql code it's just called xxx_arg1, xxx_arg2 etc...

        This method will inspect procedure in database and will grab it's
        signature and return here """

    cursor.execute("SELECT parameter_name  FROM information_schema.parameters  WHERE SPECIFIC_NAME = %s "
                   "ORDER BY ordinal_position",
                   (sproc_name,))
    return [x for x, in cursor.fetchall()]

def fn_get_sproc_output_params(cursor, sproc_name):
    """ ordinary mysql cursor.callproc() won't give us argument names
        in mysql code it's just called xxx_arg1, xxx_arg2 etc...

        This method will inspect procedure in database and will grab it's
        signature and return here """

    query = "SELECT PARAMETER_NAME FROM information_schema.parameters WHERE PARAMETER_NAME like '%oparam%' and " \
            "SPECIFIC_NAME = '{}' ORDER BY ordinal_position".format(sproc_name)

    cursor.execute(query)
    return [x for x, in cursor.fetchall()]


# execute stored procedure
def fn_call_stored_procedure(connection, sproc_name, *args, return_arg_names=False):
    """
        return_column_names - append arg_names to result
    """
    SPROC_SAMPLES = False
    try:
        cursor = connection.cursor()
        columns = None

        sproc_result_args = cursor.callproc(sproc_name, args)

        if return_arg_names:
            columns = fn_get_sproc_output_params(cursor, sproc_name)

            if SPROC_SAMPLES == True:
                sproc_params = fn_get_sproc_argnames(cursor, sproc_name)
                fn_create_sproc_samples(cursor, sproc_name, sproc_result_args, sproc_params)

            length_of_input_params = len(sproc_result_args) - len(columns)
            sproc_output_values = sproc_result_args[length_of_input_params:]
            return sproc_output_values, columns, cursor

        return sproc_result_args, cursor
    except mysql.connector.Error as error:
        if return_arg_names:
            print('Failed to execute stored procedure: {0}'.format(error))
            return str(error), columns, 400
        else:
            print('Failed to execute stored procedure: {0}'.format(error))
            return str(error), 400

def fn_create_sproc_samples(cursor, sproc_name, sproc_result_args, columns):
    oparam_names = fn_get_sproc_output_params(cursor, sproc_name)
    length_output_params = len(oparam_names)
    input_param_values = list(sproc_result_args)[:-length_output_params]
    input_param_names = columns[:-length_output_params]
    sproc_params = input_param_names + oparam_names

    list_of_input_params = ''.join(['SET @' + str(name) + ' = ' + str(input_param_values[index]) + '; \n'
                                    for index, name in enumerate(input_param_names)])

    cal_sproc = '\n,'.join(['@' + str(name) for name in sproc_params])
    cal_mysql_sproc = '\n' + 'CALL ' + sproc_name + '(' + cal_sproc + ')' + '; \n\n'

    select_output_params = '\n,'.join(['@' + str(name) for name in oparam_names]) + '; \n'
    select_mysql_sproc = 'SELECT ' + select_output_params

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_DB_PATH = os.path.join(BASE_DIR, 'logging')

    if (not os.path.exists(LOGS_DB_PATH)):
        os.makedirs(LOGS_DB_PATH)

    now = datetime.datetime.now()
    fname = format(now, '%H:%M') + '_log.txt'
    fpath = os.path.join(LOGS_DB_PATH, fname)
    file = open(fpath, 'a+')
    try:
        os.chmod(fpath, 0o777)
        file.write(list_of_input_params)
        file.write(cal_mysql_sproc)
        file.write(select_mysql_sproc)
        file.write("---------------------------------------------------------------------- \n")
    except:
        pass

    file.close()




# capture single result set from the stored procedure execution
def fn_sproc_response(cursor):
    for result in cursor.stored_results():
        return result.fetchall()

# capture multiple single result set from the stored procedure execution
def fn_sproc_multiple_result_sets_response(cursor):
    multiple_result = []
    for result in cursor.stored_results():
        res = result.fetchall()
        rowncols = [dict(zip(result.column_names, x)) for x in res]
        multiple_result.append(rowncols)
    return multiple_result

def fn_get_sproc_errors(**kwargs):
    sproc_result_args_type = isinstance(kwargs['sproc_result_args'], str)
    if sproc_result_args_type == True and kwargs['cursor'] == 400:
        return 'Failure', kwargs['sproc_result_sets'], 400
    elif kwargs["argdict"].get('oparam_err_flag') == 1 or kwargs["argdict"].get('oparam_err_flag') == None:
        return 'Failure', kwargs["argdict"], 400
    else:
        return 'Success', kwargs['cursor'], 200

def fn_sprocresult2datas(sproc_result_sets):
    ret = {}
    for n, set_ in enumerate(sproc_result_sets):
        ret["data%s"%n] = set_

    serialized = json.dumps(ret, cls=clsCustomJSONEncoder)
    deserialized = json.loads(serialized)

    return deserialized


def fn_response_data(**kwargs):
    if kwargs['method'] == "GET":

        retdict = {'status': 'Success',
                   'message': kwargs['functionality']}
        if kwargs["args"]:
            retdict["args"] = kwargs["args"]

        retdict.update(fn_sprocresult2datas(kwargs["sproc_result_sets"]))

        return retdict, kwargs['status_code']

    return {'status': 'Success',
            'message': kwargs['functionality']
            }, kwargs['status_code']


def fn_return_sproc_multiple_result_sets(**kwargs):
    if (kwargs['cursor'] == 400):
        if isinstance(kwargs.get('sproc_result_args'), str):
            return { "args": { "oparam_err_msg": kwargs.get('sproc_result_args'),
                               "oparam_err_flag": 1
                             },
                     "status": "Failure",
                     "message": "Something went wrong in db"
                   }, 404
        else:
            return {"Status": "Failure", "args": kwargs}, 404
    else:
        if kwargs["arg_names"]:
            kwargs["argdict"] = dict(zip(kwargs["arg_names"], kwargs["sproc_result_args"]))

        status, cursor_object, status_code = fn_get_sproc_errors(**kwargs)
        if status == "Failure" and status_code == 400:
            return { "args": cursor_object,
                     "status": status
                   }, status_code
        else:
            sproc_multiple_result_sets = fn_sproc_multiple_result_sets_response(cursor_object)

            if kwargs["argdict"].get('oparam_err_flag') == 1:
                return { 'status': status,
                         'err_flag': kwargs["argdict"].get('oparam_err_flag'),
                         'err_step': kwargs["argdict"].get('oparam_err_step'),
                         'err_msg': kwargs["argdict"].get('oparam_err_msg')
                       }, status_code
            else:
                return fn_response_data(sproc_result_sets=sproc_multiple_result_sets,
                                        functionality=kwargs['functionality'],
                                        args=kwargs["argdict"],
                                        method="GET",
                                        status_code=status_code)

def fn_get_sproc_lookup_errors(**kwargs):
    sproc_result_args_type = isinstance(kwargs['sproc_result_args'], str)
    if sproc_result_args_type == True and kwargs['cursor'] == 400:
        return 'Failure', kwargs['sproc_result_sets'], 400
    else:
        return 'Success', kwargs['cursor'], 200

def fn_return_sproc_lookup_result_sets(**kwargs):
    if (kwargs['cursor'] == 400):
        return {"Status": "Failure", "error": kwargs['sproc_result_args']}, 404
    else:
        if kwargs["arg_names"]:
            kwargs["argdict"] = dict(zip(kwargs["arg_names"], kwargs["sproc_result_args"]))

        status, cursor_object, status_code = fn_get_sproc_lookup_errors(**kwargs)
        if status == "Failure" and status_code == 400:
            return {'status': status, 'error': cursor_object}, status_code
        else:
            sproc_multiple_result_sets = fn_sproc_multiple_result_sets_response(cursor_object)

            return fn_response_data(sproc_result_sets=sproc_multiple_result_sets,
                                    functionality=kwargs['functionality'],
                                    args="",
                                    method="GET",
                                    status_code=status_code)

