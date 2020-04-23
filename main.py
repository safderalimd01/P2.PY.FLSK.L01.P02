from app import app
from flask import request, jsonify
import mysql.connector
from config import fn_connect_db
import json

@app.route('/productList')
def product_listing():
	try:
		db = mysql.connector.connect(user='root',password='root',host='localhost',database='tss')
		cursor = db.cursor()
		cursor.callproc('sproc_product_list')
		for result in cursor.stored_results():
			res = result.fetchall()
			rowncols = [dict(zip(result.column_names, x)) for x in res]
		return jsonify(rowncols)
	except mysql.connector.Error as error:
		return {"success":format(error)}
	finally:
		cursor.close() 
		db.close()

@app.route('/productFilter')
def product_filter():
	try:
		_json = request.json
		_product_status = _json['product_status']
		inputData = [_product_status] 
		outputData = [0, 0, ' '] # oparam_err_flag, oparam_err_step, oparam_err_msg
		bindData = inputData + outputData
		db = mysql.connector.connect(user='root',password='root',host='localhost',database='tss')
		cursor = db.cursor()

		# execute stored proc and capture results
		sproc_result_args = cursor.callproc('sproc_product_list_by_active_status',bindData)

		# list of input and output params defined for sproc on db layer
		sproc_param_names = ['iparam_product_status', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

		# assign parameter values
		argdict = dict(zip(sproc_param_names, sproc_result_args))

		for result in cursor.stored_results():
			res = result.fetchall()
			rowncols = [dict(zip(result.column_names, x)) for x in res]
		
		final = {"data1":rowncols, "Params": argdict}
		# final = [jsonify(argdict), jsonify(rowncols)]
		return final
		# return jsonify(rowncols)
		# return jsonify(argdict)

	except Exception as e:
		print(e)
	# finally:
	# 	cursor.close() 
	# 	db.close()	

@app.route('/addProduct', methods=['POST'])
def add_product():
	try:
		_json = request.json
		_product_name = _json['product_name']
		_product_status = _json['product_status']
		inputData = (_product_name, _product_status) 
		outputData = (0, 0, 0)
		bindData = inputData + outputData
		db = mysql.connector.connect(user='root',password='root',host='localhost',database='tss')
		cursor = db.cursor()

		# execute stored proc and capture results
		sproc_result_args=cursor.callproc('sproc_product_dml_ins',bindData)

		# list of input and output params defined for sproc on db layer
		sproc_param_names = ['iparam_product_name', 'iparam_active', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']

		# assign parameter values
		argdict = dict(zip(sproc_param_names, sproc_result_args))

		return jsonify(argdict)

	except Exception as e:
		print(e)
	finally:
		cursor.close() 
		db.close()	

# @app.route('/masterDB')
# def msater_db():
# 	try:
# 		_json = request.json
# 		_iparam_domain_name = _json['iparam_domain_name']
# 		_iparam_debug_sproc = _json['iparam_debug_sproc']
# 		_iparam_audit_screen_visit = _json['iparam_audit_screen_visit']
# 		inputData = [_iparam_domain_name, _iparam_debug_sproc, _iparam_audit_screen_visit] 
# 		outputData = [0, 0, 0, ' '] # oparam_login_success, oparam_err_flag, oparam_err_step, oparam_err_msg
# 		bindData = inputData + outputData
# 		db = mysql.connector.connect(user='masterdbuser',password='8749mastermysql6xx965',host='tss-aws-rds-mysql8-prod-01.careeimvtduv.ap-south-1.rds.amazonaws.com',database='sama_master')
# 		cursor = db.cursor()

# 		# execute stored proc and capture results
# 		sproc_result_args = cursor.callproc('sproc_sama_get_client_db_connnection_info_v2',bindData)

# 		# list of input and output params defined for sproc on db layer
# 		sproc_param_names = ['iparam_domain_name', 'iparam_debug_sproc', 'iparam_audit_screen_visit', 'oparam_login_success', 'oparam_err_flag', 'oparam_err_step', 'oparam_err_msg']
# 		# IN iparam_domain_name varchar(100),  
# 		# IN iparam_debug_sproc TINYINT,  
# 		# IN iparam_audit_screen_visit TINYINT,  

# 		# OUT oparam_login_success int,
# 		# OUT oparam_err_flag int,
# 		# OUT oparam_err_step varchar(100),
# 		# OUT oparam_err_msg varchar(1000))


# 		# assign parameter values
# 		argdict = dict(zip(sproc_param_names, sproc_result_args))

# 		for result in cursor.stored_results():
# 			res = result.fetchall()
# 			rowncols = [dict(zip(result.column_names, x)) for x in res]
		
# 		final = {"data1":rowncols, "Params": argdict}
# 		# final = [jsonify(argdict), jsonify(rowncols)]
# 		return final
# 		# return jsonify(rowncols)
# 		# return jsonify(argdict)

# 	except Exception as e:
# 		print(e)
# 	# finally:
# 	# 	cursor.close() 
# 	# 	db.close()	

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