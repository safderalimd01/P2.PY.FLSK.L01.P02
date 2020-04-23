from app import app
from flask import request, jsonify
import mysql.connector
from config import fn_connect_db
import json

@app.route('/productList')
def product_listing():
    try:
        db = mysql.connector.connect(user='root',password='Arun@123',host='localhost',database='Arun')
        cursor = db.cursor()
        cursor.callproc('sproc_product_list')
        for result in cursor.stored_results():
            res = result.fetchall()
            rowncols = [dict(zip(result.column_names, x)) for x in res]
        return jsonify(rowncols)
    except mysql.connector.Error as error:
        return {"success":format(error)}
    # finally:
    #     if (connection.is_connected()):
    #         cursor.close()
    #         connection.close()
    #         print("MySQL connection is closed")

@app.route('/addProduct', methods=['POST'])
def add_product():
    try:
        _json = request.json
        _product_name = _json['product_name']
        _active = _json['active']
        inputData = (_product_name, _active) 
        outputData = (0, 0, 0)
        bindData = inputData + outputData
        conn = mysql.connector.connect(user='root',password='Arun@123',host='localhost',database='Arun')
        cursor = conn.cursor()

        # store proc results
        sproc_result_args=cursor.callproc('sproc_product_dml_ins',bindData)

        # oparam names
        query = "SELECT PARAMETER_NAME FROM information_schema.parameters WHERE PARAMETER_NAME like '%oparam%' and " \
            "SPECIFIC_NAME = '{}' ORDER BY ordinal_position".format('sproc_product_dml_ins')
        cursor.execute(query)
        oparam_names=cursor.fetchall()
        # print("oparam_names" + oparam_names)
        # iparam, oparam names
        cursor.execute("SELECT parameter_name  FROM information_schema.parameters  WHERE SPECIFIC_NAME = %s ",('sproc_product_dml_ins',))
        columns = cursor.fetchall()
        
        # length of the oparams
        length_output_params = len(oparam_names)
        
        # input param values
        input_param_values = list(sproc_result_args)[:-length_output_params]
        # input param names
        input_param_names = columns[:-length_output_params]
        sproc_params = input_param_names + oparam_names

        # remove tuple to string
        sproc_param_names = []
        for row in sproc_params:
            rm_tuple=''.join(row)
            sproc_param_names.append(rm_tuple)

        # convert to dictionary
        argdict = dict(zip(sproc_param_names, sproc_result_args))
        sproc_result_args_type = isinstance(sproc_result_args, str)

        if argdict.get('oparam_err_flag') == 1:
            return jsonify(argdict)
        return jsonify(argdict)

    except Exception as e:
        print(e)
    # finally:
    #     cursor.close() 
    #     conn.close()		

@app.errorhandler(404)
def not_found(error=None):
    message = {
        'status': 404,
        'message': 'Record not found: ' + request.url,
    }
    respone = jsonify(message)
    respone.status_code = 404
    return respone
		
if __name__ == "__main__":
    app.run()