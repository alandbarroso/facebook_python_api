# Core object for facebook apis
from facebook_api.core import FacebookCoreAPI

# For dealing with client_secrets and facebook responses
import json

# Creating the login request uri
from urllib import urlencode

# Logging
import logging

class FacebookLoginAPI(FacebookCoreAPI):
	_AUTH_URI = "https://www.facebook.com/v2.1/dialog/oauth"
	_TOKEN_URI = "https://graph.facebook.com/v2.1/oauth/access_token"

	def __init__(self, client_secrets, storage, scopes, redirect_uri, http=None):
		super(FacebookLoginAPI, self).__init__(storage=storage, http=http)

		f_ = open(client_secrets, 'rb')
		secrets = json.load(f_)

		self.client_id = secrets['client_id']
		self.client_secret = secrets['client_secret']

		self.scopes = scopes

		self.redirect_uri = redirect_uri

		self.logger = logging.getLogger('FacebookLoginAPI')

	def request_login(self):
		params = {
			'client_id':self.client_id,
			'redirect_uri':self.redirect_uri,
			'scope':','.join(self.scopes)
		}

		return self._AUTH_URI + '?' + urlencode(params)

	def send_code(self, code):
		params = {
			'client_id':self.client_id,
			'client_secret':self.client_secret,
			'redirect_uri':self.redirect_uri,
			'code':code,
		}

		self.logger.info('Sending code to facebook.')

		status, response = self.login_get(url=self._TOKEN_URI, params=params)
		self.logger.info('Access token adquired.')
		access_token = response.split('=')[1] # Response in the form access_token=XXXXXXX

		self.logger.info('Storing access token.')
		self.access_token = access_token
		self.storage.save(access_token)

		# Trying to extend the access_token duration
		params = {
			'grant_type':'fb_exchange_token',
			'client_id':self.client_id,
			'client_secret':self.client_secret,
			'fb_exchange_token':self.access_token 
		}

		self.logger.info('Extending the token duration.')

		status, response = self.login_get(url=self._TOKEN_URI, params=params)
		
		self.logger.info('Access token extended.')