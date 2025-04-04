class OperationError(Exception):
	def __init__(self, http_status_code, error_message):
		self.http_status_code = http_status_code
		self.error_message = error_message

	def get_status(self):
		return self.http_status_code

	def get_message(self):
		return self.error_message
