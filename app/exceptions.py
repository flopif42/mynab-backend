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

class AccountNotExistError(Exception):
	def __str__(self):
		return "This account doesn't exist."

class AccountWrongOwnerError(Exception):
	def __str__(self):
		return "This account doesn't belong to this user."

class AccountNotEmptyError(Exception):
	def __str__(self):
		return "This account has transactions."
