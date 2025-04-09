class MyOperationError(Exception):
	pass

class InvalidParametersError(MyOperationError):
	def __init__(self, error_message="Invalid parameters."):
		self.error_message = error_message

class AccountNotFoundError(MyOperationError):
	def __init__(self):
		self.error_message = "This account doesn't exist."

class AccountPermissionError(MyOperationError):
	def __init__(self):
		self.error_message = "This account doesn't belong to this user."

class AccountNotEmptyError(MyOperationError):
	def __init__(self):
		self.error_message = "This account has transactions."


# delete this after refactoring is done
class OperationError(Exception):
	def __init__(self, http_status_code, error_message):
		self.http_status_code = http_status_code
		self.error_message = error_message

	@property
	def status(self):
		return self.http_status_code

	@property
	def message(self):
		return self.error_message

	def __str__(self):
		return f'Status code : {self.http_status_code}, Message : {self.error_message}'
