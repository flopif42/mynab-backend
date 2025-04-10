class MyOperationError(Exception):
	pass

class InvalidParametersError(MyOperationError):
	def __init__(self, error_message="Invalid parameters."):
		self.error_message = error_message

# Accounts
class AccountNotFoundError(MyOperationError):
	def __init__(self):
		self.error_message = "This account doesn't exist."

class AccountPermissionError(MyOperationError):
	def __init__(self):
		self.error_message = "This account doesn't belong to this user."

class AccountNotEmptyError(MyOperationError):
	def __init__(self):
		self.error_message = "This account has transactions."

# Payees
class PayeeNotFoundError(MyOperationError):
	def __init__(self):
		self.error_message = "This payee doesn't exist."

class PayeePermissionError(MyOperationError):
	def __init__(self):
		self.error_message = "This payee doesn't belong to this user."

class PayeeNotEmptyError(MyOperationError):
	def __init__(self):
		self.error_message = "This payee has transactions."
