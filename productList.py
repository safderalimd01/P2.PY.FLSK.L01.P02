from flask_restful import Resource
from flask import request

from executeSProc import fn_call_stored_procedure, fn_return_sproc_multiple_result_sets
from clientDBConnection import fn_make_client_db_connection
# from resources.utils.decorators.screenPermission import fn_check_screen_permission


class ClsInvProductList(Resource):

    @fn_make_client_db_connection()
    # @fn_check_screen_permission()
    def get(self, *args, **kwargs):
        try:
            # debug_sproc = int(request.headers.get('debug_sproc'))
            # audit_screen_visit = int(request.headers.get('audit_screen_visit'))

            input_params = [
                # kwargs['session_id'],
                # kwargs['user_id'],
                # kwargs['screen_id'],
                # debug_sproc,
                # audit_screen_visit
            ]
            output_params = [
                # 'oparam_err_flag',
                # 'oparam_err_step',
                # 'oparam_err_msg'
            ]
            sproc_result_args, arg_names, cursor = fn_call_stored_procedure(kwargs['client_db_connection'],
                                                                            'sproc_inv_product_grid',
                                                                            *input_params,
                                                                            *output_params,
                                                                            return_arg_names=True)

            return fn_return_sproc_multiple_result_sets(sproc_result_args=sproc_result_args,
                                                        arg_names=arg_names,
                                                        cursor=cursor,
                                                        functionality="Products List Fetched successfully")
        except Exception as e:
            return {'Error': str(e)}, 400
