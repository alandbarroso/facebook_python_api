# Facebook exceptions
from facebook_api.exceptions import MissingTokenException, ExpiredTokenException

# Libs to deal with http requests
from httplib2 import Http
from urllib import urlencode

# Libs to deal with http requests
import requests

# For dates and times
from datetime import datetime, timedelta

# For logging
import logging

# For dealing with errors 
import json

# Facebook core - just to store the http client and http methods
class FacebookCoreAPI(object):
	_RENEW_URI = "https://graph.facebook.com/v2.1/me"

	def __init__(self, storage, http=None):
		if http:
			self.http = http
		else:
			self.http = Http()

		self.storage = storage

		self.access_token = None

		self.debug_logger = logging.getLogger('FacebookCoreAPI')

	def load_access_token(self):
		try:
			access_token, token_date = self.storage.load()
		except:
			raise

		today = datetime.today()

		if today - timedelta(59) > token_date:
			raise ExpiredTokenException()

		self.access_token = access_token

	def validate_response(self, status_code, response):
		self.debug_logger.debug('Message Received:')
		self.debug_logger.debug('Status')
		self.debug_logger.debug(status_code)
		self.debug_logger.debug('Response')
		self.debug_logger.debug(response)

		if status_code == requests.codes.ok:
			return status_code, response
		else:
			content = json.loads(response)
			error_message = content['error']['message']

			raise Exception(error_message)

	def login_get(self, url, params={}):
		r = requests.get(url, params=params)

		status_code = r.status_code
		response = r.text

		try:
			status_code, response = self.validate_response(status_code, response)
		except:
			raise

		return status_code, response

	def get(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		r = requests.get(url, params=params)

		status_code = r.status_code
		response = r.text
		try:
			status_code, response = self.validate_response(status_code, response)
		except:
			raise

		return json.loads(response)

	def post(self, url, params={}, files={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		r = requests.post(url, data=params, files=files)

		status_code = r.status_code
		response = r.text		
		try:
			status_code, response = self.validate_response(status_code, response)
		except:
			raise

		return json.loads(response)

	def delete(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		r = requests.delete(url, data=params)

		status_code = r.status_code
		response = r.text
		try:
			status_code, response = self.validate_response(status_code, response)
		except:
			raise

		return json.loads(response)

	def put(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		r = requests.put(url, data=params)

		status_code = r.status_code
		response = r.text
		try:
			status, response = self.validate_response(status, response)
		except:
			raise

		return json.loads(response)

	def renew_token(self):
		self.get(self._RENEW_URI)

		self.storage.save(self.access_token)

# Abstract class of storage 
class AbstractCredentialsStorage(object):
	def save(self, access_token):
		if access_token == None:
			raise RuntimeError('access_token is None, cannot save!')

		self.access_token = access_token
		self.token_date = datetime.today()

	def load(self):
		return self.access_token, self.token_date