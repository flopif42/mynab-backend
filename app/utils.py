from flask import request
from http import HTTPStatus
from app.exceptions import InvalidParametersError

def validate_not_empty(request, parameter_name):
    """
    This function is used to check if a parameter is empty (either null, empty string or is not present in the JSON file)
    
    Return values : If the parameter is not empty, returns a stripped version of the parameter
    Exception : Raises OperationError with the 400 HTTP code if the parameter is empty
    """
    error_message = f"Parameter {parameter_name} can't be empty."
    if request.method == 'GET' or request.method == 'DELETE':
        if not parameter_name in request.args:
            raise InvalidParametersError(error_message)
        parameter = request.args.get(parameter_name)
    else:
        if not request.is_json or parameter_name not in request.json:
            raise InvalidParametersError(error_message)
        parameter = request.json[parameter_name]
    if parameter is None:
        raise InvalidParametersError(error_message)
    parameter = str(parameter).strip()
    if parameter == '':
        raise InvalidParametersError(error_message)
    return parameter
