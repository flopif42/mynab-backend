from flask import request
from http import HTTPStatus
from app.exceptions import OperationError

def validate_not_empty(request, parameter_name):
    error_message = f"Parameter {parameter_name} can't be empty."

    print(request.method)
    if request.method == 'GET':
        if not parameter_name in request.args:
            raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
        parameter = request.args.get(parameter_name)
    else:
        if not request.is_json or parameter_name not in request.json:
            raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
        parameter = request.json[parameter_name]
    if parameter is None:
        raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
    parameter = str(parameter).strip()
    if parameter == '':
        raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
    return parameter
