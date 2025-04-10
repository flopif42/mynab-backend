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

# Users
class UserInvalidCredentialsError(MyOperationError):
	def __init__(self):
		self.error_message = "The email address and password don't match."

class UserMailAdressUnavailableError(MyOperationError):
	def __init__(self):
		self.error_message = "This email address is already used."

# Parent categories
class ParentCategoryNotFoundError(MyOperationError):
	def __init__(self):
		self.error_message = "This parent category doesn't exist."

class ParentCategoryNotEmptyError(MyOperationError):
	def __init__(self):
		self.error_message = "This parent category has subcategories."

# Categories
class CategoryNotFoundError(MyOperationError):
	def __init__(self):
		self.error_message = "This category doesn't exist."

class CategoryNotEmptyError(MyOperationError):
	def __init__(self):
		self.error_message = "This category has transactions."

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
