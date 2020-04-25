from app import app
from flask import request, jsonify
import mysql.connector
from dotenv import load_dotenv
import json

import os
import mysql.connector

config = {
    'user': os.environ.get('user'),
    'password': os.environ.get('password'),
    'host': os.environ.get('host'),
    'database': os.environ.get('database')
}

@app.route('/productList')
def product_listing():
	try:
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()
			cursor.callproc('sproc_product_list')

			for result in cursor.stored_results():
				res = result.fetchall()
				rowncols = [dict(zip(result.column_names, x)) for x in res]
			close_connection(db, cursor)
			return api_success(rowncols, None, "Products listed successfully")
		else:
			return api_failure(str(db))
	except Exception as error:
		return api_failure(str(error))


@app.route('/productDetail/<int:id>', methods=['GET'])
def product_details(id):
	try:
		inputData = (id,)
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()

			# execute stored proc and capture results
			sproc_result_args=cursor.callproc('sproc_product_detail',bindData)

			for result in cursor.stored_results():
				res = result.fetchall()
				rowncols = [dict(zip(result.column_names, x)) for x in res]
			close_connection(db, cursor)
			return api_success(rowncols, None, "Products details fetched successfully")
		else:
			return api_failure(str(db))
	except Exception as e:
		return api_failure(str(e))

@app.route('/productFilter/<int:product_status>', methods=['GET'])
def product_filter(product_status):
	try:
		inputData = (product_status,)
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()

			# execute stored proc and capture results
			sproc_result_args = cursor.callproc('sproc_product_list_by_active_status',bindData)

			# list of input and output params defined for sproc on db layer
			sproc_param_names = ['iparam_product_status', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

			# assign parameter values
			argdict = dict(zip(sproc_param_names[1:], sproc_result_args[1:]))

			for result in cursor.stored_results():
				res = result.fetchall()
				rowncols = [dict(zip(result.column_names, x)) for x in res]

			close_connection(db, cursor)
			return api_success(rowncols, argdict, "Products filtered successfully")
		else:
			return api_failure(str(db))
	except Exception as e:
		return api_failure(str(e))

@app.route('/addProduct', methods=['POST'])
def add_product():
	try:
		_json = request.json
		_product_name = _json['product_name']
		_product_status = _json['product_status']
		inputData = (_product_name, _product_status)
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()

			# execute stored proc and capture results
			sproc_result_args = cursor.callproc('sproc_product_dml_ins',bindData)

			# list of input and output params defined for sproc on db layer
			sproc_param_names = ['iparam_product_name', 'iparam_active', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

			# assign parameter values
			argdict = dict(zip(sproc_param_names[2:], sproc_result_args[2:]))

			close_connection(db, cursor)
			return api_success(None, argdict, "Product saved successfully")
		else:
			return api_failure(str(db))
	except Exception as e:
		return api_failure(str(e))

@app.route('/updateProduct', methods=['PUT'])
def update_product():
	try:
		_json = request.json
		_product_id = _json['product_id']
		_product_name = _json['product_name']
		_product_status = _json['product_status']
		inputData = (_product_id, _product_name, _product_status)
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()

			# execute stored proc and capture results
			sproc_result_args=cursor.callproc('sproc_product_dml_upd',bindData)

			# list of input and output params defined for sproc on db layer
			sproc_param_names = ['iparam_product_name', 'iparam_active', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

			# assign parameter values
			argdict = dict(zip(sproc_param_names[2:], sproc_result_args[2:]))

			close_connection(db, cursor)
			return api_success(None, argdict, "Product updated successfully")
		else:
			return api_failure(str(db))
	except Exception as e:
		return api_failure(str(e))

@app.route('/deleteProduct/<int:id>', methods=['DELETE'])
def delete_product(id):
	try:
		inputData = (id,)
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user = os.environ.get('user'),
									 password = os.environ.get('password'),
									 host = os.environ.get('host'),
									 database = os.environ.get('database'))
		if not isinstance(db, str):
			cursor = db.cursor()

			# execute stored proc and capture results
			sproc_result_args=cursor.callproc('sproc_product_dml_del',bindData)

			# list of input and output params defined for sproc on db layer
			sproc_param_names = ['iparam_product_id', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

			# assign parameter values
			argdict = dict(zip(sproc_param_names[1:], sproc_result_args[1:]))

			close_connection(db, cursor)
			return api_success(None, argdict, "Product deleted successfully")
		else:
			return api_failure(str(db))
	except Exception as e:
		return api_failure(str(e))



def api_failure(error):
    respone =  {
		"api_call_status": {
			"Message": error,
			"Status": "Failure"
		}
	}, 400
    return respone


def api_success(rowncols, argdict, message):
	respone = dict()
	if argdict and argdict.get("oparam_err_flag") == 1:
		respone["api_call_status"] = {
			"Message": argdict.get("oparam_err_msg"),
			"Status": "Failure"
		}
	else:
		respone["api_call_status"] = {
			"Message": message,
			"Status": "Success"
		}


	if argdict:
		respone["sproc_output_params"] = argdict
	if isinstance(rowncols, list):
		respone["sproc_output_result"] = rowncols
	return respone, 200

def close_connection(conn, cursor):
	cursor.close()
	conn.close()

if __name__ == "__main__":
	load_dotenv()
	app.run()
