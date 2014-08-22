# Facebook exceptions
from facebook_api.exceptions import MissingTokenException, ExpiredTokenException

# Libs to deal with http requests
from httplib2 import Http
from urllib import urlencode

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

	def validate_response(self, status, response):
		self.debug_logger.debug('Message Received:')
		self.debug_logger.debug('Status')
		self.debug_logger.debug(status)
		self.debug_logger.debug('Response')
		self.debug_logger.debug(response)

		if status['status'] in ['200']:
			return status, response
		else:
			content = json.loads(response)
			error_message = content['error']['message']

			raise Exception(error_message)

	def login_get(self, url, params={}):
		if params:
			encoded_params = urlencode(params)

			d = {
				'url':url,
				'params':encoded_params
			}

			if '?' in url:
				request_url = "%(url)s&%(params)s" % d
			else:
				request_url = "%(url)s?%(params)s" % d
		else:
			request_url = url

		self.debug_logger.debug(request_url)

		status, response = self.http.request(request_url, method='GET')
		try:
			status, response = self.validate_response(status, response)
		except:
			raise

		return status, response

	def get(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		if params:
			encoded_params = urlencode(params)

			d = {
				'url':url,
				'params':encoded_params
			}

			if '?' in url:
				request_url = "%(url)s&%(params)s" % d
			else:
				request_url = "%(url)s?%(params)s" % d
		else:
			request_url = url

		self.debug_logger.debug(request_url)

		status, response = self.http.request(request_url, method='GET')
		try:
			status, response = self.validate_response(status, response)
		except:
			raise

		return json.loads(response)

	def post(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		encoded_params = urlencode(params)
		
		self.debug_logger.debug(url)

		status, response = self.http.request(url, method='POST', body=encoded_params)
		try:
			status, response = self.validate_response(status, response)
		except:
			raise

		return json.loads(response)

	def delete(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		encoded_params = urlencode(params)
		
		self.debug_logger.debug(url)

		status, response = self.http.request(url, method='DELETE', body=encoded_params)
		try:
			status, response = self.validate_response(status, response)
		except:
			raise

		return json.loads(response)

	def put(self, url, params={}):
		try:
			self.load_access_token()
		except:
			raise

		params.update({'access_token':self.access_token})

		encoded_params = urlencode(params)
		
		self.debug_logger.debug(url)

		status, response = self.http.request(url, method='PUT', body=encoded_params)
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