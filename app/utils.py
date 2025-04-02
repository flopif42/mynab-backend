from flask import request
from http import HTTPStatus
from app.exceptions import OperationError

def validate_not_empty(request, parameter_name):
    error_message = f"Parameter {parameter_name} can't be empty."
    if not request.is_json or parameter_name not in request.json:
        raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
    parameter = request.json[parameter_name]
    if parameter is None:
        raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
    parameter = str(parameter).strip()
    if parameter == '':
        raise OperationError(HTTPStatus.BAD_REQUEST, error_message)
    return parameter
