class OperationError(Exception):
	def __init__(self, http_status_code, error_message):
		self.http_status_code = http_status_code
		self.error_message = error_message
		print('init called with {http_status_code} and {error_message}')

	def get_status(self):
		return self.http_status_code

	def get_message(self):
		return self.error_message

	def __str__(self):
		return f('Status code : {self.http_status_code}, Message : {self.error_message}')
