# Abstract Storage
from facebook_api.core import AbstractCredentialsStorage

# Exception
from facebook_api.exceptions import MissingTokenException

# To read and write inside the file storage
import json

# To use date
from datetime import datetime

class FileCredentialsStorage(AbstractCredentialsStorage):
	def __init__(self, filename, access_token=None):
		self.filename = filename

		if access_token:
			self.save(access_token)

	def save(self, access_token):
		super(FileCredentialsStorage, self).save(access_token)

		f_ = open(self.filename, 'wb')

		content = {'access_token':self.access_token,
					'token_date':self.token_date.strftime('%Y-%m-%d')}

		f_.write(json.dumps(content))

		f_.close()

	def load(self):
		try:
			f_ = open(self.filename, 'rb')

			content = json.load(f_)
			self.access_token = content['access_token']
			self.token_date = datetime.strptime(content['token_date'], '%Y-%m-%d')

			f_.close()

			return super(FileCredentialsStorage, self).load()
		except:
			raise MissingTokenException()