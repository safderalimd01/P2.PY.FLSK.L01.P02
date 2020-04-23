from app import app
import mysql.connector
from flask import request, jsonify
import json
import os
from flask import request

@app.route('/productList')
def product_listing():
	try:
		conn = mysql.connector.connect(host='localhost', database='tss', user='root', password='root')
		cursor = conn.cursor()
		cursor.callproc('sproc_product_list')
		for result in cursor.stored_results():
			res = result.fetchall()
			rowncols = [dict(zip(result.column_names, x)) for x in res]
		return jsonify(rowncols)
	except Exception as error:
		print("Failed to execute stored procedure: {}".format(error))
	finally:
		cursor.close() 
		conn.close()

@app.route('/addProduct', methods=['POST'])
def add_product():
	try:
		_json = request.json
		_product_name = _json['product_name']
		_active = _json['active']

		conn = mysql.connector.connect(host='localhost', database='tss', user='root', password='root')
		cursor = conn.cursor()

		inputData = (_product_name, _active) 
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		sproc_result_args = cursor.callproc('sproc_product_dml_ins',bindData)
		for result in cursor.stored_results():
			print(result.fetchall())

		 # get list of oparam names
		query = "SELECT PARAMETER_NAME FROM information_schema.parameters WHERE PARAMETER_NAME like '%oparam%' and SPECIFIC_NAME = '{}' ORDER BY ordinal_position".format('sproc_product_dml_ins')
		cursor.execute(query)
		oparam_names=cursor.fetchall()
		print("Oparams : % " %(oparam_names))

		# # get list of iparam and oparam names together
		# cursor.execute("SELECT parameter_name FROM information_schema.parameters WHERE SPECIFIC_NAME = %s ",('sproc_product_dml_ins',))
		# columns = cursor.fetchall()
		# print('all params:' {}).format

		#  # sort params
        # length_output_params = len(oparam_names)
        # input_param_values = list(sproc_result_args)[:-length_output_params]
        # input_param_names = columns[:-length_output_params]
        # sproc_params = input_param_names + oparam_names

		# args = (_product_name, _active, 0, 0, (0, 'CHAR'))
		# result_args = cursor.callproc('sproc_product_dml_ins', args)
		# return result_args
	except Exception as error:
		print("Failed to execute stored procedure: {}".format(error))
	# finally:
	# 	cursor.close() 
	# 	conn.close()


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