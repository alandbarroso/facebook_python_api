class MissingTokenException(Exception):
	def __str__(self):
		return 'Token missing! Run the oauth login!'

class ExpiredTokenException(Exception):
	def __str__(self):
		return 'Token has expired! Please rerun the oauth!'